import streamlit as st
import os
from scripts.main import main as process_audio
from scripts.main import mix_tracks

st.set_page_config(page_title="自動音訊處理工具", page_icon="")
st.title("自動音訊處理工具")

st.markdown("請選擇使用的功能：")

mode = st.radio("選擇功能模式", ["A 模式：分離人聲與伴奏", "B 模式：合併兩個音訊檔案"])

# 建立必要資料夾
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

if mode == "A 模式：分離人聲與伴奏":
    st.markdown("上傳一個音訊檔案，進行分離或合併處理。")
    uploaded_file = st.file_uploader("請上傳音訊檔案（.wav 或 .mp3）", type=["wav", "mp3"])

    if uploaded_file:
        input_path = os.path.join("input", uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"已上傳：{uploaded_file.name}")

        if st.button("開始處理"):
            with st.spinner("處理中，請稍候..."):
                process_audio(input_path, is_vocal=False)
            st.success("處理完成！")

            st.markdown("### 下載結果：")
            output_files = {
                "人聲": "final_vocals.wav",
                "伴奏": "final_accompaniment.wav",
                "混音": "final_mix.wav"
            }

            for label, fname in output_files.items():
                path = os.path.join("output", fname)
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button(label=label, data=f, file_name=fname)

elif mode == "B 模式：合併兩個音訊檔案":
    st.markdown("上傳兩個音訊檔案（例如伴奏與主唱），進行混音合併。")

    vocal_file = st.file_uploader("請上傳主唱音檔（.wav 或 .mp3）", type=["wav", "mp3"], key="vocal")
    accomp_file = st.file_uploader("請上傳伴奏音檔（.wav 或 .mp3）", type=["wav", "mp3"], key="accomp")

    vocal_gain = st.slider("主唱音量調整（dB）", -20, 20, 20)
    accomp_gain = st.slider("伴奏音量調整（dB）", -20, 20, 0)

    if vocal_file and accomp_file:
        vocal_path = os.path.join("input", vocal_file.name)
        accomp_path = os.path.join("input", accomp_file.name)

        with open(vocal_path, "wb") as f:
            f.write(vocal_file.getbuffer())
        with open(accomp_path, "wb") as f:
            f.write(accomp_file.getbuffer())

        st.success("已成功上傳兩個檔案。")

        if st.button("開始合併"):
            with st.spinner("合併中，請稍候..."):
                output_mix_path = os.path.join("output", "custom_mix.wav")
                mix_tracks(vocal_path, accomp_path, output_mix_path, vocal_gain, accomp_gain)
            st.success("合併完成！")

            with open(output_mix_path, "rb") as f:
                st.download_button(label="下載合併後音檔", data=f, file_name="custom_mix.wav")
