import express from 'express'
import http from 'http'
import { Server } from 'socket.io'
import cors from 'cors'
import dotenv from 'dotenv'
import axios from 'axios'
import FormData from 'form-data'
import fs from 'fs'
import path from 'path'
import calendarRouter from './routes/calendar.js'

dotenv.config()

const PORT = process.env.PORT || 5000
const FRONTEND_ORIGIN = process.env.FRONTEND_ORIGIN || 'http://localhost:5173'
const PYTHON_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000'
const PYTHON_API_KEY = process.env.PYTHON_SERVICE_API_KEY || null
const DATA_DIR = path.resolve(process.env.DATA_DIR || './data')
const MEMORY_FILE = path.join(DATA_DIR, 'memory.json')
const MEMORY_LIMIT = 100

fs.mkdirSync(DATA_DIR, { recursive: true })

// --- Memory persistence -----------------------------------------------
function loadMemory() {
  try {
    return JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'))
  } catch {
    return []
  }
}

function saveMemory(memory) {
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory.slice(-MEMORY_LIMIT), null, 2))
}

let memory = loadMemory()

// --- App setup -----------------------------------------------------------
const app = express()
app.use(cors({ origin: FRONTEND_ORIGIN }))
app.use(express.json())
app.use('/api/calendar', calendarRouter)

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', ai: 'local', memory: memory.length })
})

app.get('/api/memory', (req, res) => {
  res.json(memory.slice(-20))
})

app.delete('/api/memory', (req, res) => {
  memory = []
  saveMemory(memory)
  res.json({ ok: true })
})

const server = http.createServer(app)
const io = new Server(server, { cors: { origin: FRONTEND_ORIGIN } })

// --- Realtime voice pipeline ----------------------------------------------
async function handleFinalAudioChunk(socket, arrayBuffer) {
  socket.emit('ai_thinking')

  const form = new FormData()
  form.append('file', Buffer.from(arrayBuffer), { filename: 'audio.webm', contentType: 'audio/webm' })
  form.append('history', JSON.stringify(memory.slice(-10)))

  const headers = form.getHeaders()
  if (PYTHON_API_KEY) headers['X-API-Key'] = PYTHON_API_KEY

  try {
    const resp = await axios.post(`${PYTHON_URL}/process-voice`, form, { headers, timeout: 90000 })
    const { transcript, text, tool, audio_url } = resp.data

    memory.push({ user: transcript, ai: text, tool: tool || null, timestamp: new Date().toISOString() })
    saveMemory(memory)

    socket.emit('final_transcript', transcript)
    socket.emit('ai_response', {
      text,
      userText: transcript,
      tool,
      audioUrl: audio_url ? `${PYTHON_URL}${audio_url}` : null,
    })
  } catch (err) {
    console.error('[voice pipeline]', err.response?.data || err.message)
    socket.emit('ai_response', {
      text: 'I could not reach the local AI service. Check that the Python service and Ollama are running.',
      userText: 'error',
      tool: null,
      audioUrl: null,
    })
  }
}

io.on('connection', (socket) => {
  socket.emit('memory_snapshot', memory.slice(-20))
  socket.on('audio_chunk_stream', () => socket.emit('partial_transcript', 'Listening…'))
  socket.on('audio_chunk_final', (arrayBuffer) => handleFinalAudioChunk(socket, arrayBuffer))
})

server.listen(PORT, () => console.log(`JARVIS gateway listening on ${PORT}`))
