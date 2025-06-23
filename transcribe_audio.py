import whisper

def transcribe(audio_path):
    model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
    result = model.transcribe(audio_path)

    # Print transcript
    print("\n[📝 Transcription Result]")
    print(result['text'])

    return result

if __name__ == "__main__":
    audio_file = "audio/sample_audio.wav"  # Make sure this path matches your extracted audio
    transcribe(audio_file)
