from youtube_transcript_api import YouTubeTranscriptApi
from faster_whisper import WhisperModel
import re
import os

# Initialize whisper model lazily to save RAM
_whisper_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        print("[*] Loading Faster-Whisper model... this might take a moment on first run.")
        # Using base model for lightweight speed on CPU/Local
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def get_youtube_transcript(url: str) -> str:
    """Fetches the transcript of a YouTube video given its URL."""
    try:
        # Extract video ID
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            return "Error: Could not extract YouTube Video ID from the provided URL."
        video_id = video_id_match.group(1)
        
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        full_text = []
        for segment in transcript_list:
            full_text.append(segment['text'])
            
        combined_text = " ".join(full_text)
        
        # Truncate if insanely long (prevent context exhaustion)
        if len(combined_text) > 15000:
            combined_text = combined_text[:15000] + "... [TRUNCATED]"
            
        return f"--- YOUTUBE TRANSCRIPT ---\n{combined_text}"
        
    except Exception as e:
        return f"Error fetching YouTube transcript: {e}"

def transcribe_audio(file_path: str) -> str:
    """Uses a local Whisper model to transcribe an audio file to text."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
        
    try:
        model = _get_whisper()
        segments, info = model.transcribe(file_path, beam_size=5)
        
        full_text = []
        for segment in segments:
            full_text.append(segment.text)
            
        return " ".join(full_text).strip()
    except Exception as e:
        return f"Error transcribing audio with Whisper: {e}"
