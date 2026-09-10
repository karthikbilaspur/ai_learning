import os
print("Loading Whisper model... (first run downloads ~150MB)")
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("Whisper loaded")
except Exception as e:
    print(f"Whisper load failed {e}, will use mock")
    model = None

def transcribe_audio(file_path: str) -> str:
    if model:
        try:
            segments, info = model.transcribe(file_path, beam_size=5, language="en")
            text = " ".join([s.text for s in segments])
            print(f"Transcribed: {text}")
            return text.strip()
        except Exception as e:
            print(f"STT error {e}")
    return "What is my schedule today?"
