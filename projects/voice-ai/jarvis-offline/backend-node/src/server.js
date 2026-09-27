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
const app = express()
app.use(cors({ origin: process.env.FRONTEND_ORIGIN || 'http://localhost:5173' }))
app.use(express.json())
app.use('/api/calendar', calendarRouter)
const server = http.createServer(app)
const io = new Server(server, { cors: { origin: process.env.FRONTEND_ORIGIN || 'http://localhost:5173' } })
const PYTHON_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000'
const DATA_DIR = path.resolve(process.env.DATA_DIR || './data')
const MEMORY_FILE = path.join(DATA_DIR, 'memory.json')
fs.mkdirSync(DATA_DIR, { recursive: true })
function loadMemory(){ try { return JSON.parse(fs.readFileSync(MEMORY_FILE,'utf8')) } catch { return [] } }
function saveMemory(){ fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory.slice(-100), null, 2)) }
let memory = loadMemory()

app.get('/api/health', (req,res)=>res.json({status:'ok', ai:'local', memory:memory.length}))
app.get('/api/memory', (req,res)=>res.json(memory.slice(-20)))
app.delete('/api/memory', (req,res)=>{ memory=[]; saveMemory(); res.json({ok:true}) })

io.on('connection', socket=>{
  socket.emit('memory_snapshot', memory.slice(-20))
  socket.on('audio_chunk_stream', ()=>socket.emit('partial_transcript','Listening…'))
  socket.on('audio_chunk_final', async (arrayBuffer)=>{
    try {
      socket.emit('ai_thinking')
      const form = new FormData()
      form.append('file', Buffer.from(arrayBuffer), { filename:'audio.webm', contentType:'audio/webm' })
      form.append('history', JSON.stringify(memory.slice(-10)))
      const resp = await axios.post(`${PYTHON_URL}/process-voice`, form, {headers:form.getHeaders(), timeout:90000})
      const { transcript, text, tool, audio_url } = resp.data
      const item={user:transcript, ai:text, tool:tool||null, timestamp:new Date().toISOString()}
      memory.push(item); saveMemory()
      socket.emit('final_transcript', transcript)
      socket.emit('ai_response', {text,userText:transcript,tool,audioUrl:audio_url?`${PYTHON_URL}${audio_url}`:null})
    } catch(e) {
      console.error(e.response?.data || e.message)
      socket.emit('ai_response',{text:'I could not reach the local AI service. Check that the Python service and Ollama are running.',userText:'error',tool:null,audioUrl:null})
    }
  })
})
const PORT=process.env.PORT||5000
server.listen(PORT,()=>console.log(`JARVIS gateway listening on ${PORT}`))
