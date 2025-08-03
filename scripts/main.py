import os
import argparse
import subprocess
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def reduce_noise(input_path, output_path):
    y, sr = librosa.load(input_path, sr=None)
    reduced_noise = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, reduced_noise, sr)

def simple_autotune(input_path, output_path):
    y, sr = librosa.load(input_path, sr=None)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=0)  # optional correction
    sf.write(output_path, y_shifted, sr)

def normalize_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    normalized = audio.apply_gain(-audio.max_dBFS)
    normalized.export(output_path, format="wav")

def process_vocal(input_path):
    denoised = f"{OUTPUT_DIR}/vocal_denoised.wav"
    autotuned = f"{OUTPUT_DIR}/vocal_autotuned.wav"
    final = f"{OUTPUT_DIR}/final_vocals.wav"

    reduce_noise(input_path, denoised)
    simple_autotune(denoised, autotuned)
    normalize_audio(autotuned, final)

    return final

def mix_tracks(vocal_path, accompaniment_path, output_path):
    vocal = AudioSegment.from_file(vocal_path)
    accomp = AudioSegment.from_file(accompaniment_path)
    mix = accomp.overlay(vocal)
    mix.export(output_path, format="wav")

def combine_accompaniment(tracks_folder):
    mix = None
    for fname in os.listdir(tracks_folder):
        if fname.endswith(".wav") and "vocals" not in fname.lower():
            path = os.path.join(tracks_folder, fname)
            track = AudioSegment.from_file(path)
            mix = track if mix is None else mix.overlay(track)
    return mix

def main(audio_path, is_vocal):
    if is_vocal:
        # 若上傳的是已分離或純人聲檔，直接拷貝到 output 不做任何處理
        output_vocal = os.path.join(OUTPUT_DIR, "final_vocals.wav")
        AudioSegment.from_file(audio_path).export(output_vocal, format="wav")
        print(f"Vocal saved at: {output_vocal}")
        return

    subprocess.run(["demucs", audio_path])

    song_name = os.path.splitext(os.path.basename(audio_path))[0]
    split_dir = os.path.join("separated", "htdemucs", song_name)

    vocal_path = os.path.join(split_dir, "vocals.wav")
    if not os.path.exists(vocal_path):
        raise FileNotFoundError("找不到 vocals.wav")

    # 合成所有非 vocals.wav 的檔案
    accompaniment_mix = combine_accompaniment(split_dir)
    accomp_path = os.path.join(OUTPUT_DIR, "final_accompaniment.wav")
    accompaniment_mix.export(accomp_path, format="wav")

    # 直接使用未處理的 vocals.wav
    output_vocal = os.path.join(OUTPUT_DIR, "final_vocals.wav")
    AudioSegment.from_file(vocal_path).export(output_vocal, format="wav")

    # 混音：未處理 vocals + 自動合成的伴奏
    mix_tracks(output_vocal, accomp_path, os.path.join(OUTPUT_DIR, "final_mix.wav"))
    print("所有檔案已輸出到 output 資料夾")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to input audio file")
    parser.add_argument("--vocal", action="store_true", help="If input is a clean vocal file")
    args = parser.parse_args()
    main(args.input, args.vocal)
