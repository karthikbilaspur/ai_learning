# JARVIS Lite — Local Voice AI Assistant

A portfolio-ready local voice assistant built as a modular system: React UI, Node.js real-time gateway, Python AI service, local Whisper STT, Ollama LLM, Piper TTS, and optional Google Calendar integration.

## Architecture

React → Socket.IO → Node.js gateway → Python AI service → Whisper / Ollama / Piper
                                             ↘ tool layer → Google Calendar

## Highlights

- Local speech-to-text with faster-whisper
- Local LLM inference with Ollama
- Local text-to-speech with Piper
- Structured JSON tool routing from the LLM
- Persistent local conversation memory
- Persistent Google OAuth token storage
- Calendar read + event creation API
- Real-time Socket.IO events and polished responsive UI
- Clear health and memory endpoints

## Important note
The AI inference path is local, but this project is **not completely offline** when weather or Google Calendar is used. Calendar requires internet access and OAuth. Weather is an optional online integration.

## Setup

### 1. Ollama
Install Ollama and run:

```bash
ollama pull llama3.1:8b
ollama serve
```

### 2. Python service

```bash
cd backend-python
python -m venv .venv
# activate the environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Piper needs a compatible `.onnx` voice model. Set `PIPER_VOICE=/absolute/path/to/voice.onnx` if the model is not in the working directory.

### 3. Node gateway

```bash
cd backend-node
cp .env.example .env
npm install
npm run dev
```

For Google Calendar, create OAuth credentials in Google Cloud and set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## API

- `GET /api/health` — gateway health
- `GET /api/memory` — recent memory
- `DELETE /api/memory` — clear memory
- `GET /api/calendar/auth` — start Google OAuth
- `GET /api/calendar/status` — calendar connection status
- `GET /api/calendar/events/today` — today's events
- `POST /api/calendar/events` — create an event with `{title,start,end,description?,location?}`

## Portfolio talking points

1. Separation of concerns across React, Node, and Python services.
2. Real-time bidirectional audio workflow with Socket.IO.
3. Local AI inference to reduce API dependency and improve privacy.
4. Structured tool execution instead of string-matching every request.
5. OAuth2 integration with a real external productivity API.
6. Persistent state and explicit health/error handling.

## Limitations

- The local LLM must be installed separately.
- Whisper model startup can take time on CPU.
- Calendar token storage is local JSON and should be replaced by encrypted storage for multi-user production deployments.
- The assistant currently expects English speech.
