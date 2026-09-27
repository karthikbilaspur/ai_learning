from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, json, uuid
from .stt import transcribe_audio
from .llm import get_ai_response
from .tts import synthesize_speech
app = FastAPI(title="JARVIS Offline Brain")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def health():
    return {"status":"Offline brain online", "stt":"faster-whisper", "llm":"ollama llama3.1", "tts":"piper"}
@app.post("/process-voice")
async def process_voice(file: UploadFile = File(...), history: str = Form("[]")):
    temp_path = f"/tmp/{uuid.uuid4()}.webm"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    transcript = transcribe_audio(temp_path)
    history_list = json.loads(history) if history else []
    ai_text, tool_used = get_ai_response(transcript, history_list)
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = f"static/audio/{audio_filename}"
    synthesize_speech(ai_text, audio_path)
    return {"transcript": transcript, "text": ai_text, "tool": tool_used, "audio_url": f"/static/audio/{audio_filename}"}
