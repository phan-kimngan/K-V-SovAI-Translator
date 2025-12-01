import streamlit as st
from gtts import gTTS
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase



API_kor_to_vie = "https://tenacious-von-occludent.ngrok-free.dev/kor2vie"
API_vie_to_kor = "https://tenacious-von-occludent.ngrok-free.dev/vie2kor"      
# ==============================
# 1. PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="K-V SovAI Translator",
    page_icon="🇰🇷🇻🇳",
    layout="centered"
)

# 💡 CSS MOBILE: giữ 2 cột, tối ưu khoảng trắng
# 💡 CSS MOBILE: giữ 2 cột, tối ưu khoảng trắng

st.markdown("""
<style>

@media (max-width: 600px) {

    /* ===== Đưa label Korean / Vietnamese sát box ===== */
    div[data-testid="column"] > div:nth-child(1) {
        margin-bottom: 4px !important;
    }

    /* chính xác target label */
    div[data-testid="column"] > div > div > div {
        margin-bottom: 6px !important;
        margin-top: 2px !important;
    }

    /* ===== ĐẶT SWAP VÀO CHÍNH GIỮA ===== */

    /* khối chứa cột giữa */
    div[data-testid="column"]:nth-child(2) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }





    /* ===== giảm khoảng trắng extra giữa các phần tử ===== */


    div[data-testid="stVerticalBlock"]{
        gap: 6px !important;
        margin-top: 2px !important;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

@media (max-width: 600px) {

    /* Kéo toàn bộ content lên trên */
    .main > div:first-child {
        padding-top: 0px !important;
    }

    /* Kéo title lên cao hơn */
    div[style*='K-V SovAI Translator'] {
        margin-top: -10px !important;
    }

    /* Căn giữa nút icon 🔊 và ↔️ */
    .stButton > button {
        display: flex;
        justify-content: center !important;
        align-items: center !important;
    }



    /* Xử lý khoảng cách dưới Vietnamese */
    div[style*='font-size:25px'] {
        margin-bottom: 0px !important;
    }


}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@media (max-width: 600px) {
    /* giữ 2 cột song song nếu có thể */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
    }
    div[data-testid="column"] {
        display: inline-block !important;
        width: 49% !important;
        vertical-align: top;
    }

    /* thu gọn padding của container chính */
    .block-container {
        padding-left: 1px !important;
        padding-right: 1px !important;
        padding-top: 1px !important;
        padding-bottom: 1px !important;
    }

    /* header gọn hơn một chút */
    h2 {
        margin-top: 30px !important;
        margin-bottom: 30px !important;
        font-size: 24px !important;
    }

    /* nút bấm nhỏ gọn hơn */
    .stButton > button {
        padding: 6px 12px !important;
        font-size: 14px !important;
        align-items: center !important;
    }

    /* history box gọn lại */
    .history-box {
        margin-bottom: 4px !important;
        padding: 6px !important;
    }
}
</style>
""", unsafe_allow_html=True)
# ==============================
# 2. SESSION STATE
# ==============================
if "mode" not in st.session_state:
    st.session_state.mode = "vi_to_kr"

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "update_trigger" not in st.session_state:
    st.session_state.update_trigger = 0
    
if "translation" not in st.session_state:
    st.session_state.translation = ""

if "history" not in st.session_state:
    st.session_state.history = []


# ==============================
# 3. CSS
# ==============================

# khoảng cách 2 box trong mobile
st.markdown(
    """
    <style>
    .swap-container {
        position: relative;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>

    /* Nền gradient tím pastel → xanh nhạt */
    body, .stApp {
        background: linear-gradient(145deg, #C9C3FF, #B8D7FF) !important;
        color: #FFFFFF;
    }

    /* Tiêu đề */
    h2 {
        color: #FFFFFF !important;
        font-weight: 800;
        text-shadow: 0px 1px 4px rgba(0,0,0,0.18);
    }

    /* Textbox trắng */
    textarea {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
        #border: rgba(255,255,255,0.6) !important;
        border-radius: 14px !important;
        padding: 12px !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08);
        height: 220px !important;
        font-size: 17px !important;
    }

    /* Buttons */
    .stButton > button {
    background-color: rgba(255,255,255,0.55) !important;  /* đậm từ 0.28 → 0.55 */
    color: #1E1E1E !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255,255,255,0.8) !important;
    padding: 10px 22px;
    border-radius: 10px;
    backdrop-filter: blur(8px);
    box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }

    .stButton > button:hover {
    background-color: rgba(255,255,255,0.8) !important;
    border: 1px solid #FFFFFF !important;
    transform: scale(1.07);
    box-shadow: 0 4px 10px rgba(0,0,0,0.22);
    }


    /* Màu chữ tiêu đề app */
    h2 {
        color: #111111 !important;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# 4. HEADER
# ==============================
st.markdown(
    """
    <h2 style='text-align:center; color:#1E3A8A'>
        🇰🇷 K-V SovAI Translator 🇻🇳
    </h2>
    """,
    unsafe_allow_html=True
)

# ==============================
# 5. LAYOUT

col1, col_center, col2 = st.columns([1, 0.25, 1])
#col1, col2 = st.columns(2)

# ==============================
# 6. SWAP
# ==============================
with col_center:
    #st.markdown("<div class='swap-container'>", unsafe_allow_html=True)
    st.markdown(f"<div style='align-items: center !important; margin-top: -30px !important; margin-bottom: -30px !important;'>", unsafe_allow_html=True)
    swap_clicked = st.button("⬆️⬇️", key="swap_button")
    st.markdown("</div>", unsafe_allow_html=True)

if swap_clicked:
    st.session_state.mode = "kr_to_vi" if st.session_state.mode == "vi_to_kr" else "vi_to_kr"

    old_in = st.session_state.input_text
    old_out = st.session_state.translation

    st.session_state.input_text = old_out
    st.session_state.translation = old_in

# ==============================
# 7. LABEL CONFIG
# ==============================
mode = st.session_state.mode
if mode == "vi_to_kr":
    left_label = "Vietnamese"
    right_label = "Korean"
    src_tts_lang = "vi"
    tgt_tts_lang = "ko"
    translate_func = API_vie_to_kor
else:
    left_label = "Korean"
    right_label = "Vietnamese"
    src_tts_lang = "ko"
    tgt_tts_lang = "vi"
    translate_func = API_kor_to_vie

# ==============================
# 8. LEFT PANEL
# ==============================
with col1:
    st.markdown(f"<div style='color: #000000;font-size:20px; font-weight:600; margin-bottom:25px'>{left_label}</div>", unsafe_allow_html=True)

    input_text = st.text_area(
        " ",
        st.session_state.input_text,
        height=200,
        key="input_text",
        label_visibility="collapsed"
    )
        

    components.html(
"""
<style>

#holdToTalk {
    width: 48px !important;
    height: 48px !important;
    font-size: 18px !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.65) !important;
    color: #1E1E1E !important;
    border: 1px solid rgba(255,255,255,0.9) !important;
    display:flex !important;
    justify-content:center !important;
    align-items:center !important;
    padding: 0 !important;
    margin: 0 !important;
    margin-left: -4px !important;
    box-shadow: 0 3px 6px rgba(0,0,0,0.13) !important;
    flex: 0 0 auto !important;
}

#copyVoiceBtn {
    width: 28px;
    height: 28px;
    font-size: 14px;
    border-radius: 8px;
    background: rgba(255,255,255,0.65);
    border:1px solid rgba(255,255,255,0.9);
    display:none;
    justify-content:center;
    align-items:center;
    margin-left: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.12);
    flex: 0 0 auto !important;
}

#status {
    flex: 1 1 auto !important;
    max-width: 100% !important;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}


/* khi đang ghi âm */
#holdToTalk.recording {
    background: rgba(255,80,80,0.9);
    color:white;
    border:1px solid rgba(255,255,255,1);
    animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 4px rgba(255,80,80,0.3); }
  50% { box-shadow: 0 0 12px rgba(255,20,20,1); }
 100% { box-shadow: 0 0 4px rgba(255,80,80,0.3); }
}
</style>

<div style="display:flex; flex-direction:row; align-items:center; gap:8px;">
    <button id="holdToTalk">🎤</button>
    <p id="status" style="font-size:12px;color:#444;margin-top:4px;"></p>
    <button id="copyVoiceBtn">📋</button>
</div>

<script>
let mediaRecorder;
let chunks = [];
let recording = false;
let startTime = 0;

btn = document.getElementById("holdToTalk");
statusBox = document.getElementById("status");
copyBtn = document.getElementById("copyVoiceBtn");

btn.addEventListener("mousedown", startRecording);
btn.addEventListener("mouseup", stopRecording);
btn.addEventListener("touchstart", startRecording);
btn.addEventListener("touchend", stopRecording);

function enableCopyBtn(){
  copyBtn.style.display="flex";
}

copyBtn.addEventListener("click", function(){
    navigator.clipboard.writeText(statusBox.innerText);
    copyBtn.innerHTML = "✔";
    setTimeout(()=> copyBtn.innerHTML="📋", 1200)
});

function startRecording(e) {
    if (recording) return;
    recording = true;
    chunks = [];
    startTime = Date.now();

    btn.classList.add("recording");
    statusBox.innerHTML = "🎙️...";
    statusBox.style.color = "#ff3b3b";

    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.start();
    });
}

async function stopRecording(e) {
    if (!recording) return;
    recording = false;

    btn.classList.remove("recording");
    statusBox.innerHTML = "⏳...";
    statusBox.style.color = "#ffaa00";
    mediaRecorder.stop();

    mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        let formData = new FormData();
        formData.append("file", blob, "voice.webm");

        let r = await fetch("https://tenacious-von-occludent.ngrok-free.dev/voice2text", {
            method: "POST",
            body: formData,
            mode: "cors",
            headers: {"ngrok-skip-browser-warning": "1" }
        });

        let raw = await r.text();
        let res = JSON.parse(raw);
        statusBox.innerHTML = res.text;
        statusBox.style.color = "#111111";

        enableCopyBtn();

        window.parent.postMessage(
            { type: "voice-text", text: res.text },
            "*"
        );
    }
}
</script>
""",
height=60
)


    if st.button("🔊", key="speak_input"):
        if input_text.strip():
            tts = gTTS(input_text, lang=src_tts_lang)
            tts.save("input_tts.mp3")
            with open("input_tts.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")  


# ==============================
# 9. RIGHT PANEL
# ==============================
with col2:
    st.markdown(f"<div style='color: #000000; font-size:20px; font-weight:600;'>{right_label}</div>", unsafe_allow_html=True)

    st.text_area(
        " ",
        st.session_state.translation,
        height=200,
        key="output_box"
    )

    if st.button("🔊", key="speak_output"):
        if st.session_state.translation.strip():
            tts = gTTS(st.session_state.translation, lang=tgt_tts_lang)
            tts.save("output_tts.mp3")
            with open("output_tts.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ==============================
# 10. TRANSLATE
# ==============================
if st.button("🌐 Translate", use_container_width=True):
    text = st.session_state.input_text.strip()
    if text:
        with st.spinner("Translating... ⏳"):
            #result = translate_func(text)
            result = requests.get(translate_func, params={"text": text})
            result = result.json()["result"]

            st.session_state.translation = result

            # SAVE HISTORY
            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": st.session_state.mode,
                "src": text,
                "tgt": result
            })

        st.rerun()

# ==============================
# 12. HISTORY VIEW
# ==============================
#st.markdown("<div style='color: #000000; font-size:25px; font-weight:600; margin-top:10px; margin-bottom:20px'>🕘 History</div>", unsafe_allow_html=True)

# ==============================
# 12. HISTORY VIEW
# ==============================
# 12. HISTORY VIEW
# ==============================
st.markdown("<div style='color: #000000; font-size:25px; font-weight:600; margin-top:15px;'>🕘 History</div>", unsafe_allow_html=True)

# CSS layout 2 nút sát 2 bên
st.markdown("""
<style>
.hist-btn-container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    gap: 10px;
}

.hist-btn-container button {
    width: 100% !important;
}

/* MOBILE FIX */
@media (max-width: 600px) {
    .hist-btn-container {
        gap: 6px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
    }
}
</style>
""", unsafe_allow_html=True)

# RENDER 2 NÚT KHÔNG QUA st.columns()
st.markdown("<div class='hist-btn-container'>", unsafe_allow_html=True)

clear = st.button("🧹 Clear all history")
export = st.button("💾 Export to CSV")

st.markdown("</div>", unsafe_allow_html=True)

# LOGIC NÚT
if clear:
    st.session_state.history = []
    st.rerun()

if export:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df.to_csv("translation_history.csv", index=False)
        with open("translation_history.csv", "rb") as f:
            st.download_button(
                label="⬇️ Download CSV file",
                data=f,
                file_name="translation_history.csv",
                mime="text/csv"
            )
    else:
        st.warning("⚠️ Không có dữ liệu để export")





# SHOW HISTORY LIST
for item in reversed(st.session_state.history):

    if item["mode"] == "vi_to_kr":
        direction = "🇻🇳 Vietnamese → 🇰🇷 Korean"
    else:
        direction = "🇰🇷 Korean → 🇻🇳 Vietnamese"

    st.markdown(
        f"""
        <div class="history-box" style="
            padding:8px; 
            background:rgba(255,255,255,0.45);
            border: 1px solid rgba(0,0,0,0.18);
            border-radius:10px;
            margin-bottom:8px;
            font-size:13px;
            line-height:1.4;
            color: #000000
        ">
            <span style="font-size:11px; color:#000000;">{item['time']}</span><br>
            <span style="font-size:13px; color:#000000; font-weight:600;">{direction}</span><br><br>
            <span style="font-size:13px; color:#000000"><b>Input:</b><br>{item['src']}</span><br><br>
            <span style="font-size:13px; color:#000000"><b>Output:</b><br>{item['tgt']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )




# 11. FOOTER
# ==============================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>© 2025 K-V SovAI Translator</p>", unsafe_allow_html=True)
