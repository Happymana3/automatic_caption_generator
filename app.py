import os
import subprocess
import streamlit as st
from datetime import timedelta
import whisper
import srt
from moviepy.editor import VideoFileClip

# --- Step 1: Audio Extraction ---
def extract_audio(video_path, audio_output_path):
    try:
        video = VideoFileClip(video_path)
        if video.audio:
            video.audio.write_audiofile(audio_output_path)
            return True
        else:
            st.error("No audio track found in the video.")
            return False
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return False

# --- Step 2: Transcription using Whisper ---
def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")  # You can choose 'tiny', 'small', etc.
        result = model.transcribe(audio_path)
        return result
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

# --- Step 3: Generate SRT File ---
def generate_srt(transcription_result):
    try:
        subtitles = []
        for i, seg in enumerate(transcription_result.get('segments', [])):
            subtitle = srt.Subtitle(
                index=i + 1,
                start=timedelta(seconds=seg['start']),
                end=timedelta(seconds=seg['end']),
                content=seg['text'].strip()
            )
            subtitles.append(subtitle)
        return srt.compose(subtitles)
    except Exception as e:
        st.error(f"Error generating SRT: {e}")
        return ""

# --- Step 4: Burn Subtitles using FFmpeg ---
def burn_subtitles(video_path, srt_relative_path, output_video, ffmpeg_path):
    # This uses the working command with relative path for SRT
    video_full = os.path.abspath(video_path)
    output_full = os.path.abspath(output_video)
    command = f'"{ffmpeg_path}" -i "{video_full}" -vf "subtitles={srt_relative_path}" "{output_full}"'
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error burning subtitles: {e}")
        return False

# --- Main Streamlit App ---
def main():
    st.title("AI-Powered Video Caption Generator")
    st.write("Upload a video to generate and burn captions onto it.")

    # File uploader for video
    uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mov"])
    if uploaded_video:
        # Save the uploaded video
        video_path = "videos/uploaded_video.mp4"
        os.makedirs("videos", exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())
        st.video(video_path)

        if st.button("Generate Captions"):
            # Step 1: Extract Audio
            os.makedirs("audio", exist_ok=True)
            audio_path = "audio/uploaded_audio.wav"
            st.write("Extracting audio...")
            if not extract_audio(video_path, audio_path):
                return

            # Step 2: Transcribe Audio
            st.write("Transcribing audio...")
            transcription_result = transcribe_audio(audio_path)
            if not transcription_result:
                return
            st.write("Transcription Result:")
            st.write(transcription_result.get("text", ""))

            # Step 3: Generate SRT File
            srt_content = generate_srt(transcription_result)
            os.makedirs("captions", exist_ok=True)
            srt_path = "captions/uploaded_output.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            st.success("SRT file generated.")

            # Step 4: Burn Subtitles onto Video
            ffmpeg_path = r"C:\ffmpeg-2025-03-24-git-cbbc927a67-essentials_build\bin\ffmpeg.exe"  # Update to your FFmpeg path
            st.write("Burning subtitles onto video...")
            if burn_subtitles(video_path, srt_path, "videos/uploaded_output_video.mp4", ffmpeg_path):
                st.success("Video with burned-in captions generated!")
                st.video("videos/uploaded_output_video.mp4")

if __name__ == "__main__":
    main()
