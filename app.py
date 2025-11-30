import streamlit as st
from gtts import gTTS
import pandas as pd
from datetime import datetime

#from predict import translate_kor_to_vie
#from predict_2 import translate_vie_to_kor
def translate_kor_to_vie(text):
    return text
def translate_vie_to_kor(text):
    return text
    
       
# ==============================
# 1. PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="K-V SovAI Translator",
    page_icon="🇰🇷🇻🇳",
    layout="centered"
)
st.markdown("""
<style>
@media (max-width: 600px) {
    div[data-testid="column"] {
        display: inline-block !important;
        width: 49% !important;
        vertical-align: top;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# st.markdown("""
# <style>
# @media (max-width: 600px) {
#     .css-ocqkz7 {
#         flex-direction: row !important;
#     }
#     .stColumn {
#         width: 50% !important;
#         min-width: 50% !important;
#     }
#     .block-container {
#         width: 100vw !important;
#     }
# }
# </style>
# """, unsafe_allow_html=True)
# st.markdown("""
# <style>
# textarea {
#     font-size: 16px !important;
# }
# </style>
# """, unsafe_allow_html=True)

# ==============================
# 2. SESSION STATE
# ==============================
if "mode" not in st.session_state:
    st.session_state.mode = "vi_to_kr"

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "translation" not in st.session_state:
    st.session_state.translation = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 3. CSS
# ==============================
st.markdown("""
<style>
/* MOBILE SPACING IMPROVEMENT */
@media (max-width: 600px) {

    /* thu nhỏ padding container */
    .block-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    /* giảm khoảng cách giữa 2 box text */
    textarea {
        height: 160px !important; 
        font-size: 16px !important;
    }

    /* giảm margin history box */
    .history-box {
        margin-bottom: 4px !important;
        padding: 6px !important;
    }

    /* thu gọn chiều cao nút Translate */
    .stButton > button {
        padding: 8px 12px !important;
        font-size: 14px !important;
    }

    /* giảm khoảng cách phía trên & dưới label Vietnamese / Korean */
    div[style*='font-size:25px'] {
        font-size: 19px !important;
        margin-bottom: 4px !important;
        margin-top: 4px !important;
    }

    /* giảm chiều cao swap arrow button */
    .swap-container {
        height: 40px !important;
    }
}
</style>
""", unsafe_allow_html=True)



# khaong cach 2 box trong mobile
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
        border: 1px solid rgba(255,255,255,0.6) !important;
        border-radius: 14px !important;
        padding: 12px !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08);
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
st.markdown(
    """
    <style>

    /* XÓA VIỀN KHUNG LỚN HEADER */
    .stApp header, .stApp div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* XÓA KHUNG NỀN NHẬN DIỆN CỦA STREAMLIT CHO TITLE */
    div[data-testid="stMarkdownContainer"] h2 {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* XÓA NỀN CHO NHÃN Vietnamese / Korean */
    div[data-testid="stMarkdownContainer"] div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* TARGET LABELS TRỰC TIẾP */
    div[role="textbox"]::placeholder,
    div[role="textbox"],
    .css-1uixxvy,
    .css-1r6slb0 {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* XÓA KHUNG Ở GIỮA */
    .swap-container,
    div[data-testid="column"] div div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* XÓA VIỀN TRỪ TEXTAREA */
    textarea {
        border: 1px solid #9EC8D1 !important;
        border-radius: 12px !important;
        background: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)
# 4. HEADER
# ==============================
st.markdown(
    """
    <h2 style='text-align:center; color:#1E3A8A;'>
        🇰🇷 K-V SovAI Translator 🇻🇳
    </h2>
    """,
    unsafe_allow_html=True
)

# ==============================
# 5. LAYOUT
# ==============================
col1, col_center, col2 = st.columns([1, 0.25, 1])
#col1, col2 = st.columns(2)

# ==============================
# 6. SWAP
# ==============================
with col_center:
    st.markdown("<div class='swap-container'>", unsafe_allow_html=True)
    swap_clicked = st.button("↔️", key="swap_button")
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
    translate_func = translate_vie_to_kor
else:
    left_label = "Korean"
    right_label = "Vietnamese"
    src_tts_lang = "ko"
    tgt_tts_lang = "vi"
    translate_func = translate_kor_to_vie

# ==============================
# 8. LEFT PANEL
# ==============================
with col1:
    st.markdown(f"<div style='color: #000000;font-size:25px; font-weight:600;'>{left_label}</div>", unsafe_allow_html=True)

    if "temp_voice_text" in st.session_state and st.session_state.temp_voice_text:
        default_text = st.session_state.temp_voice_text
        st.session_state.temp_voice_text = ""   # reset
    else:
        default_text = st.session_state.input_text

    input_text = st.text_area(
        "",
        key="input_text",
        height=200,
        value=default_text
    )

    #colA, colB = st.columns([1, 1])
    #with colA:
    #    if st.button("🔊", key="speak_input"):
    #        if input_text.strip():
    #            tts = gTTS(input_text, lang=src_tts_lang)
    #            tts.save("input_tts.mp3")
    #            st.audio("input_tts.mp3")

    #with colB:
    #    if st.button("🎤", key="voice_input"):
    #        text = record_and_transcribe(language=src_tts_lang)
    #        st.session_state["temp_voice_text"] = text
    #        st.rerun()
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
    st.markdown(f"<div style='color: #000000; font-size:25px; font-weight:600;'>{right_label}</div>", unsafe_allow_html=True)

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
            result = translate_func(text)
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


# ==============================
# 12. HISTORY VIEW
# ==============================
st.markdown("<div style='color: #000000; font-size:25px; font-weight:600; margin-top:10px; margin-bottom:20px'>🕘 History</div>", unsafe_allow_html=True)

colH1, colH2 = st.columns([1, 1])

with colH1:
    if st.button("🧹 Clear all history"):
        st.session_state.history = []
        st.rerun()

with colH2:
    if st.button("💾 Export history to CSV"):
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
