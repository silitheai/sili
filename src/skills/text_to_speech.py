from gtts import gTTS
import os

def text_to_speech(text: str, filename: str = 'output_audio.mp3', lang: str = 'en') -> str:
    """Converts a block of text into a locally saved audio file (.mp3) using Google TTS."""
    if not text.strip():
        return "Error: Cannot generate speech from empty text."
        
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save output in the current working directory / tmp by default for easy access
        save_path = os.path.join(os.path.dirname(__file__), '..', '..', filename)
        
        tts.save(save_path)
        return f"Successfully generated speech audio file. Saved at: {os.path.abspath(save_path)}"
        
    except Exception as e:
        return f"Error converting text to speech: {str(e)}"
