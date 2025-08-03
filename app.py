
import streamlit as st
import os
# import subprocess
from scripts.main import main as process_audio

st.set_page_config(page_title="自動音訊處理工具", page_icon="")
st.title("自動音訊處理工具")
st.markdown("上傳一個音訊檔案，進行分割成人聲與伴奏。")

# 建立必要資料夾
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

uploaded_file = st.file_uploader("請上傳音訊檔案（.wav 或 .mp3）", type=["wav", "mp3"])
# is_vocal = st.checkbox("這是純人聲檔案嗎？", value=False)
is_vocal = False

if uploaded_file:
    input_path = os.path.join("input", uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"已上傳：{uploaded_file.name}")

    if st.button("開始處理"):
        with st.spinner("處理中，請稍候..."):
            process_audio(input_path, is_vocal)
        st.success("處理完成！")

        st.markdown("### 下載結果：")
        output_files = {
            # "重新混音合成（人聲 + 伴奏）": "final_mix.wav",
            "人聲": "final_vocals.wav",
            "伴奏": "final_accompaniment.wav"
        }

        for label, fname in output_files.items():
            path = os.path.join("output", fname)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(label=label, data=f, file_name=fname)
