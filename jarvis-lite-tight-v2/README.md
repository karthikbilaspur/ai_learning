# JARVIS Lite — Local Voice AI Assistant

A local voice assistant built as a modular system: React UI, Node.js real-time gateway,
Python AI service, local Whisper STT, Ollama LLM, Piper TTS, and optional Google Calendar
integration.

## Architecture

```
React → Socket.IO → Node.js gateway → Python AI service → Whisper / Ollama / Piper
                                             ↘ tool layer → Google Calendar (via gateway)
```

## Highlights

- Local speech-to-text with faster-whisper
- Local LLM inference with Ollama, with structured JSON tool-calling
- Local text-to-speech with Piper
- Persistent local conversation memory
- Google Calendar read + event creation, via OAuth
- Real-time Socket.IO events and a responsive UI
- Health, memory, and calendar-status endpoints
- Unit tests around the tool-call parsing and tool dispatch logic

## Honest scope: what this is and isn't

This is a **single-user, local-network** project, not a production multi-tenant service.
Specifically:

- **No end-user auth.** Anyone who can reach the Node gateway can read/clear memory or
  trigger voice processing. An optional shared-secret key (`SERVICE_API_KEY`) is available
  between Node and Python (see `.env.example` in each backend), but there's no user login.
- **Calendar tokens are single-account.** `google-tokens.json` holds one Google account's
  OAuth tokens in plaintext on disk. Fine for a personal local assistant; not fine for
  multiple users or a public deployment.
- **STT/TTS fallbacks are explicit, not silent.** If Whisper or Piper aren't installed/
  configured, the API responses include `transcript_mocked` / `audio_mocked` flags rather
  than pretending everything worked — check those flags if voice output looks "stuck."
- **Not fully offline.** Calendar requires internet + OAuth; weather (`wttr.in`) is an
  optional online call.

## Setup

### 1. Ollama

```bash
ollama pull llama3.1:8b
ollama serve
```

### 2. Python service

```bash
cd backend-python
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Piper needs a compatible `.onnx` voice model. Set `PIPER_VOICE=/absolute/path/to/voice.onnx`
in `.env` if the model isn't in the working directory.

Run the tests:

```bash
pytest tests/
```

### 3. Node gateway

```bash
cd backend-node
cp .env.example .env
npm install
npm run dev
```

For Google Calendar, create OAuth credentials in Google Cloud and set `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` in `.env`.

### 4. Frontend

```bash
cd frontend
cp .env.example .env
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
- `POST /api/calendar/events` — create an event with `{title, start, end, description?, location?}`

## Project structure

```
backend-node/
  src/server.js           Socket.IO + REST gateway, memory persistence
  src/routes/calendar.js  Google OAuth + Calendar API routes
backend-python/
  app/main.py             FastAPI entrypoint, ties STT → LLM → TTS together
  app/stt.py               faster-whisper wrapper
  app/llm.py               Ollama calls, fast-path answers, tool-call parsing
  app/tools.py              Tool implementations (time, weather, notes, calendar)
  app/tts.py                Piper wrapper
  tests/                    pytest suite for llm.py / tools.py
frontend/
  src/App.jsx                Top-level layout
  src/useJarvis.js           Socket + recording state, as a hook
  src/components/            VoiceConsole, MemoryPanel, Visualizer
```

## Talking points

1. Separation of concerns across React, Node, and Python services.
2. Real-time bidirectional audio workflow with Socket.IO.
3. Local AI inference to reduce API dependency and improve privacy.
4. Structured tool execution instead of string-matching every request, with tests around
   the JSON-extraction logic (the most brittle part of hand-rolled tool-calling).
5. OAuth2 integration with a real external productivity API.
6. Explicit fallback/mock signaling instead of silent failure masking.

## Known limitations / next steps

- The local LLM must be installed separately (Ollama).
- Whisper model startup can take time on CPU.
- Calendar token storage is local JSON; swap for encrypted, per-user storage for any
  multi-user or public deployment.
- The assistant currently expects English speech.
- No end-user authentication layer yet (see "Honest scope" above).
