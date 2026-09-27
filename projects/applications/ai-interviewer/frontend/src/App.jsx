import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ROLES = ['Fullstack', 'Frontend', 'Backend', 'AI Engineer']
const LEVELS = ['Junior', 'Mid', 'Senior']

function getSessionId() {
  let id = localStorage.getItem('interviewer_session_id')
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('interviewer_session_id', id)
  }
  return id
}

export default function App() {
  const [role, setRole] = useState('Fullstack')
  const [level, setLevel] = useState('Mid')
  const [status, setStatus] = useState('idle') // idle, asking, listening, evaluating
  const [question, setQuestion] = useState(null)
  const [transcript, setTranscript] = useState('')
  const [evaluation, setEvaluation] = useState(null)
  const [history, setHistory] = useState([])
  const [memory, setMemory] = useState({ strengths: [], weaknesses: [] })
  const [sessionScore, setSessionScore] = useState(0)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState(null)
  const mediaRef = useRef(null)
  const sessionId = useRef(getSessionId())

  useEffect(() => {
    fetch(`${API}/memory?session_id=${sessionId.current}`).then(r => r.json()).then(setMemory).catch(() => {})
    fetch(`${API}/status`).then(r => r.json()).then(setBackendStatus).catch(() => {})
  }, [])

  const startInterview = async () => {
    setStatus('asking')
    setError(null)
    try {
      const res = await axios.post(`${API}/start`, { role, level, session_id: sessionId.current })
      setQuestion(res.data)
      setTranscript('')
      setEvaluation(null)
      speak(res.data.question_text, res.data.audio_url)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to start interview.')
    }
    setStatus('idle')
  }

  const speak = (text, audioUrl) => {
    if (audioUrl) {
      const a = new Audio(`${API}${audioUrl}`)
      a.play()
    } else if ('speechSynthesis' in window) {
      const u = new SpeechSynthesisUtterance(text)
      speechSynthesis.speak(u)
    }
  }

  const startRecording = async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRef.current = rec
      const chunks = []
      rec.ondataavailable = e => chunks.push(e.data)
      rec.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        const form = new FormData()
        form.append('file', blob, 'answer.webm')
        form.append('question_id', question.question_id)
        form.append('role', role)
        form.append('level', level)
        form.append('session_id', sessionId.current)
        setStatus('evaluating')
        try {
          const res = await axios.post(`${API}/answer`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
          setTranscript(res.data.transcript)
          setEvaluation(res.data.evaluation)
          setHistory(h => [...h, { q: question.question_text, a: res.data.transcript, eval: res.data.evaluation }])
          setSessionScore(s => s + res.data.evaluation.score)
          setMemory(res.data.memory)
          setQuestion(res.data.next_question)
          if (res.data.next_question) {
            speak(res.data.next_question.question_text, res.data.next_question.audio_url)
          }
        } catch (e) {
          // e.g. STT failure — surfaced explicitly instead of a fake transcript
          setError(e?.response?.data?.detail || 'Something went wrong scoring your answer. Try recording again.')
        }
        setStatus('idle')
      }
      rec.start()
      setStatus('listening')
    } catch (e) {
      setError('Could not access the microphone. Check browser permissions.')
      setStatus('idle')
    }
  }
  const stopRecording = () => mediaRef.current?.stop()

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: 20, display: 'flex', gap: 20 }}>
      <div style={{ width: 320 }}>
        <h2>AI Interviewer <span style={{ color: '#7c3aed' }}>ADV</span></h2>

        {error && (
          <div className="card" style={{ marginBottom: 12, borderColor: '#ef4444', background: '#2a1414' }}>
            <b style={{ color: '#ef4444' }}>Error</b>
            <p style={{ margin: '4px 0 0', fontSize: 13 }}>{error}</p>
          </div>
        )}

        <div className="card">
          <label>Role</label>
          <select value={role} onChange={e => setRole(e.target.value)} style={{ width: '100%', padding: 8, background: '#0a0a0f', color: 'white', marginTop: 4 }}>
            {ROLES.map(r => <option key={r}>{r}</option>)}
          </select>
          <label style={{ marginTop: 12, display: 'block' }}>Level</label>
          <select value={level} onChange={e => setLevel(e.target.value)} style={{ width: '100%', padding: 8, background: '#0a0a0f', color: 'white', marginTop: 4 }}>
            {LEVELS.map(l => <option key={l}>{l}</option>)}
          </select>
          <button className="btn" style={{ marginTop: 12, width: '100%' }} onClick={startInterview}>Start Interview</button>
          <div style={{ marginTop: 16 }}>
            <small>Session Score: {history.length ? (sessionScore / history.length).toFixed(1) + '/10' : '0'}</small>
            <div style={{ marginTop: 8 }}>
              <b>Memory (this session)</b>
              <div style={{ fontSize: 12, opacity: 0.8 }}>
                Strengths: {memory.strengths?.join(', ') || 'none yet'}<br />
                Weaknesses: {memory.weaknesses?.join(', ') || 'none yet'}
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ marginTop: 12 }}>
          <h4>Stack (active this run)</h4>
          {backendStatus ? (
            <small>
              {backendStatus.langgraph_active ? '✅' : '⚠️ fallback runner —'} LangGraph orchestration<br />
              {backendStatus.bm25 ? '✅' : '❌'} BM25 lexical retrieval<br />
              {backendStatus.chroma_vector ? '✅' : '❌'} Chroma vector retrieval<br />
              {backendStatus.cross_encoder_rerank ? '✅' : '❌'} Cross-encoder rerank<br />
              Whisper STT + Piper/browser TTS · SQLite session memory
            </small>
          ) : <small>Checking backend status…</small>}
        </div>
      </div>

      <div style={{ flex: 1 }}>
        {question && <div className="card" style={{ borderColor: '#7c3aed' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, opacity: 0.6 }}>{question.category} • {question.difficulty}</span>
            <span style={{ fontSize: 12 }}>{question.question_id}</span>
          </div>
          <h3 style={{ marginTop: 8 }}>{question.question_text}</h3>
          {question.hints && <small style={{ opacity: 0.6 }}>Hint: {question.hints}</small>}
          <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
            <button className={`btn ${status === 'listening' ? 'rec' : ''}`} onMouseDown={startRecording} onMouseUp={stopRecording} onTouchStart={startRecording} onTouchEnd={stopRecording}>
              {status === 'listening' ? '● Listening' : '🎤 Hold to Answer'}
            </button>
            <span style={{ opacity: 0.6, paddingTop: 10 }}>Status: {status}</span>
          </div>
        </div>}

        {transcript && <div className="card" style={{ marginTop: 12 }}><b>Your Answer:</b><p>{transcript}</p></div>}

        {evaluation && <div className="card" style={{ marginTop: 12, borderLeft: `4px solid ${evaluation.score >= 7 ? '#22c55e' : evaluation.score >= 5 ? '#f59e0b' : '#ef4444'}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <h3 className={evaluation.score >= 7 ? 'score-good' : evaluation.score >= 5 ? 'score-mid' : 'score-bad'}>Score: {evaluation.score}/10</h3>
            <small>{evaluation.verdict}{!evaluation.llm_scored && ' (heuristic — LLM unavailable)'}</small>
          </div>
          <div style={{ marginTop: 8 }}><b>Feedback:</b><ReactMarkdown>{evaluation.feedback}</ReactMarkdown></div>
          <div style={{ marginTop: 8 }}>
            <b>Better Answer:</b>
            <div style={{ background: '#0a0a0f', padding: 12, borderRadius: 8 }}><ReactMarkdown>{evaluation.better_answer}</ReactMarkdown></div>
          </div>
          {evaluation.follow_up && <div style={{ marginTop: 8 }}><b>Follow-up:</b> {evaluation.follow_up}</div>}
        </div>}

        <div style={{ marginTop: 16 }}>
          <h4>History</h4>
          {history.map((h, i) => (
            <div key={i} className="card" style={{ marginTop: 8, padding: 12 }}>
              <small>Q{i + 1}: {h.q}</small><br />
              <small>A: {h.a.slice(0, 120)}...</small><br />
              <b className={h.eval.score >= 7 ? 'score-good' : h.eval.score >= 5 ? 'score-mid' : 'score-bad'}>{h.eval.score}/10</b>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
