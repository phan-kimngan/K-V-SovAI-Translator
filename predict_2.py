from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, re, unicodedata
model_path = "./skt-ax3.1light-vie-kor-qlora"

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

model = AutoModelForCausalLM.from_pretrained(
model_path,
load_in_4bit=True,
torch_dtype=torch.float16,
device_map="auto"
)
model.eval()
def preprocesing(generated, task = None):
# 1) Gỡ prompt rác/instruction lặp
    generated = re.sub(
    r"(?is)(translate\s+the\s+following\s+korean\s+sentence\s+into\s+vietnamese[:：]?\s*|"
    r"you\s+are\s+a\s+helpful\s+translator\s+that\s+translates[:：]?\s*|"
    r"are\s+a\s+helpful\s+translator\s+that\s+translates[:：]?\s*|"
    r"that\s+translates[:：]?\s*|"
    r"to\s+vietnamese[:：]?\s*|"
    r"vietnamese[:：]?\s*|"
    r"sentence\s+in[:：]?\s*|"
    r"in[:：]?\s*|"
    r"following\s+korean\s+sentence\s+into\s+vietnamese[:：]?\s*|"
    r"user[:：]?|assistant[:：]?|input[:：]?|output[:：]?|korean[:：]?|english[:：]?|the\s+)?",
    "",
    generated,
    )

    # 2) Loại ký tự vô hình/BOM/space đặc biệt + ký tự lỗi
    generated = generated.replace("\ufeff", "")
    generated = re.sub(r"[\u200B-\u200D\uFEFF\u00A0]+", "", generated)  # zero-width, NBSP
    if task =="kor_vie":
        generated = re.sub(r"[가-힣ㄱ-ㅎㅏ-ㅣ�]+", "", generated)            # nếu còn sót Hàn + ký tự lỗi
    if task =="vie_kor":
        generated = re.sub(r"[A-Za-zÀ-ỿà-ỹĂăÂâĐđÊêÔôƠơƯư�]+", "", generated)

    # 3) Thu gọn whitespace
    generated = re.sub(r"[\r\n\t]+", " ", generated)
    generated = re.sub(r"\s+", " ", generated).strip()

    # 4) XÓA ĐÁNH SỐ/CHẤM ĐẦU DÒNG – làm nhiều vòng cho chắc
    #    Bao phủ: "10.", "10 .", "200, 1 .", "1)", "2 -", "3:" ...
    patterns_head = [
    # Cụm số có thể có danh sách kèm dấu sau nó (1. | 1) | 1: | 200, 1 .)
    r"^\s*(?:\d+(?:\s*[,，]\s*\d+)*)(?:[\.\u3002,，:：;\)\]-–—])\s*",
    # Lặp nhiều lần (ví dụ "1) 2) ...")
    r"^(?:\d+(?:[\.\u3002,，:：;\)\]-–—])\s*)+",
    # Trường hợp còn sót: một hoặc nhiều số rồi đến chấm/ký tự liền nhau không có space
    r"^\s*\d+[\.\u3002:：;\)\]-–—]+",
    # Dấu câu/space rác đầu câu
    r"^[\.\u3002,，:：;!\?…·•\(\)\[\]\{\}\-–—\"“”\'\s]+",
    # Token tiếng Anh rác đầu câu (nếu còn)
    r"^(?:korean|the|english|sentence|input|output|are|a|helpful|translator|that|translates)\b[\s\.\,:\-–—;!\?\"“”\'\)]*",
    ]
    # Áp dụng lặp cho tới khi không thay đổi nữa (tối đa 5 vòng)
    for _ in range(5):
        old = generated
        for pat in patterns_head:
            generated = re.sub(pat, "", generated, flags=re.IGNORECASE)
        generated = generated.lstrip()
        if generated == old:
            break

    # 5) Dọn lại khoảng trắng cuối cùng (không đụng dấu câu cuối)
    generated = re.sub(r"\s+", " ", generated).strip()

    # 6) Viết hoa chữ cái đầu nếu có
    if generated:
        generated = generated[0].upper() + generated[1:]
    return generated
def translate_vie_to_kor(text: str, max_new_tokens=80) -> str:
    """Dịch từ tiếng Hàn sang tiếng Việt bằng mô hình đã fine-tune"""
    if not text.strip():
        return ""

    messages = [
        {"role": "system", "content": "You are a helpful translator that translates Vietnamese to Korean."},
        {"role": "user", "content": f"Translate the following Vietnamese sentence into Korean:\n\n{text}"},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.8,            
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

    input_len = inputs["attention_mask"].sum(dim=1).item()
    gen_ids = outputs[0][input_len:]
    generated = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

    # --- Làm sạch kết quả ---
    generated = unicodedata.normalize("NFKC", generated)
    generated = preprocesing(generated, task = "vie_kor")
    #generated = re.sub(r"\s+", " ", generated).strip()
    return generated

#a = translate_vie_to_kor("Nên bạn chỉ cần đổi đúng 1 dòng là hết lỗi.")
#print('ket qua la', a)
