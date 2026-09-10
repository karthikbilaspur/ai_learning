import json
import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .llm import get_ai_response
from .stt import transcribe_audio
from .tts import synthesize_speech

# Optional shared-secret auth. Unset by default (matches the original
# project's "trusted local network" assumption) but easy to turn on: set
# SERVICE_API_KEY and have the Node gateway send it as X-API-Key.
API_KEY = os.getenv("SERVICE_API_KEY")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="JARVIS Offline Brain")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def _check_api_key(x_api_key: str | None) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


@app.get("/")
def health():
    return {"status": "Offline brain online", "stt": "faster-whisper", "llm": "ollama llama3.1", "tts": "piper"}


@app.post("/process-voice")
async def process_voice(
    file: UploadFile = File(...),
    history: str = Form("[]"),
    x_api_key: str | None = Header(default=None),
):
    _check_api_key(x_api_key)

    temp_path = f"/tmp/{uuid.uuid4()}.webm"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        transcription = transcribe_audio(temp_path)
    finally:
        # Don't let a leftover temp file linger past this request.
        try:
            os.remove(temp_path)
        except OSError:
            pass

    try:
        history_list = json.loads(history) if history else []
    except json.JSONDecodeError:
        history_list = []

    ai_text, tool_used = get_ai_response(transcription["text"], history_list)

    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = f"static/audio/{audio_filename}"
    audio_result = synthesize_speech(ai_text, audio_path)

    return {
        "transcript": transcription["text"],
        "transcript_mocked": transcription["mocked"],
        "text": ai_text,
        "tool": tool_used,
        "audio_url": f"/static/audio/{audio_filename}",
        "audio_mocked": audio_result["mocked"],
    }
