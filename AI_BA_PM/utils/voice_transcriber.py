"""
Utility: Voice Transcription
Converts recorded audio bytes to text using Google's free Speech Recognition API.
No API key needed — uses Google's public web speech endpoint.
"""
import io
import speech_recognition as sr


def transcribe_audio(audio_bytes: bytes, language: str = "en-IN") -> tuple[str, str]:
    """
    Convert audio bytes (WAV format from st.audio_input) to text.

    Args:
        audio_bytes: Raw audio bytes from Streamlit's st.audio_input()
        language: BCP-47 language code. Defaults to en-IN (Indian English).
                  Other options: 'en-US', 'hi-IN', 'en-GB'

    Returns:
        (transcribed_text, status_message)
        status: 'success' | 'no_speech' | 'error'
    """
    recognizer = sr.Recognizer()
    # Adjust sensitivity — lower = more sensitive to quiet audio
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            # Read up to 5 minutes of audio
            audio_data = recognizer.record(source, duration=None)

        text = recognizer.recognize_google(audio_data, language=language)
        return text.strip(), "success"

    except sr.UnknownValueError:
        return "", "no_speech"
    except sr.RequestError as e:
        return "", f"error: Could not reach Google Speech API — {e}"
    except Exception as e:
        return "", f"error: {e}"


SUPPORTED_LANGUAGES = {
    "🇮🇳 English (India)":   "en-IN",
    "🇺🇸 English (US)":      "en-US",
    "🇬🇧 English (UK)":      "en-GB",
    "🇮🇳 Hindi":             "hi-IN",
    "🇮🇳 Gujarati":          "gu-IN",
    "🇮🇳 Marathi":           "mr-IN",
    "🇮🇳 Tamil":             "ta-IN",
    "🇮🇳 Telugu":            "te-IN",
    "🇮🇳 Malayalam":         "ml-IN",
    "🇦🇪 Arabic":            "ar-AE",
}
