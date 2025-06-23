import os
import openai
import srt

# Set your OpenAI API key (ensure it's set in your environment for safety)
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set your OPENAI_API_KEY environment variable.")

def translate_text_openai(text, target_language="Spanish"):
    """
    Uses OpenAI's ChatCompletion API to translate a piece of text into the target language.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a translation engine that translates text into {target_language}."},
                {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
            ],
            temperature=0
        )
        translation = response.choices[0].message.content.strip()
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback: return original text

def translate_srt_openai(srt_content, target_language="Spanish"):
    """
    Translates each subtitle in an SRT content to the target language.
    """
    subtitles = list(srt.parse(srt_content))
    for subtitle in subtitles:
        translated_text = translate_text_openai(subtitle.content, target_language)
        subtitle.content = translated_text
    return srt.compose(subtitles)

def srt_to_webvtt(srt_content):
    """
    Converts SRT content to WebVTT format.
    """
    # Parse the SRT content into subtitle objects
    subtitles = list(srt.parse(srt_content))
    # Compose back into SRT format
    srt_formatted = srt.compose(subtitles)
    # WebVTT requires a header and uses dots instead of commas in timecodes.
    webvtt_content = "WEBVTT\n\n" + srt_formatted.replace(",", ".")
    return webvtt_content

def main():
    # File paths (adjust as needed)
    input_srt = "captions/output.srt"  # Original SRT generated from transcription
    translated_srt_path = "captions/output_spanish.srt"
    webvtt_path = "captions/output.vtt"

    target_language = "Spanish"  # Change target language if desired

    # Read the original SRT content
    try:
        with open(input_srt, "r", encoding="utf-8") as f:
            original_srt = f.read()
    except FileNotFoundError:
        print(f"Input SRT file not found: {input_srt}")
        return

    # Translate the SRT content using OpenAI
    print("Translating SRT content...")
    translated_srt = translate_srt_openai(original_srt, target_language)

    # Save the translated SRT file
    with open(translated_srt_path, "w", encoding="utf-8") as f:
        f.write(translated_srt)
    print(f"Translated SRT saved as {translated_srt_path}")

    # Convert the original SRT to WebVTT
    print("Converting original SRT to WebVTT format...")
    webvtt_content = srt_to_webvtt(original_srt)
    with open(webvtt_path, "w", encoding="utf-8") as f:
        f.write(webvtt_content)
    print(f"WebVTT file generated as {webvtt_path}")

if __name__ == "__main__":
    main()
