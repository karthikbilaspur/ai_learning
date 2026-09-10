import { useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'

const API = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:5000'

// Single shared socket instance for the app's lifetime.
const socket = io(API)

export function useJarvis() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [partial, setPartial] = useState('')
  const [response, setResponse] = useState('')
  const [history, setHistory] = useState([])
  const [status, setStatus] = useState('idle')
  const [calendarConnected, setCalendarConnected] = useState(false)
  const [error, setError] = useState('')

  const recorder = useRef(null)
  const chunks = useRef([])
  const audio = useRef(null)

  useEffect(() => {
    const onPartial = (text) => setPartial(text)
    const onFinal = (text) => {
      setTranscript(text)
      setPartial('')
    }
    const onThinking = () => {
      setStatus('thinking')
      setError('')
    }
    const onMemorySnapshot = (snapshot) => setHistory(snapshot)
    const onAiResponse = (data) => {
      setResponse(data.text)
      setHistory((prev) => [...prev.slice(-19), { user: data.userText, ai: data.text, tool: data.tool }])
      setStatus('speaking')

      if (data.audioUrl) {
        audio.current = new Audio(data.audioUrl)
        audio.current.onended = () => setStatus('idle')
        audio.current.onerror = () => setStatus('idle')
        audio.current.play().catch(() => setStatus('idle'))
      } else {
        speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(data.text)
        utterance.onend = () => setStatus('idle')
        speechSynthesis.speak(utterance)
      }
    }

    socket.on('partial_transcript', onPartial)
    socket.on('final_transcript', onFinal)
    socket.on('ai_thinking', onThinking)
    socket.on('memory_snapshot', onMemorySnapshot)
    socket.on('ai_response', onAiResponse)

    fetch(`${API}/api/calendar/status`)
      .then((r) => r.json())
      .then((d) => setCalendarConnected(d.connected))
      .catch(() => setError('Gateway unavailable'))

    return () => {
      socket.off('partial_transcript', onPartial)
      socket.off('final_transcript', onFinal)
      socket.off('ai_thinking', onThinking)
      socket.off('memory_snapshot', onMemorySnapshot)
      socket.off('ai_response', onAiResponse)
    }
  }, [])

  async function start() {
    if (listening) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunks.current = []
      recorder.current = mediaRecorder

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size) chunks.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        setListening(false)
        setStatus('thinking')
        const buffer = await new Blob(chunks.current, { type: 'audio/webm' }).arrayBuffer()
        socket.emit('audio_chunk_final', buffer)
      }

      mediaRecorder.start()
      setListening(true)
      setStatus('listening')
      socket.emit('audio_chunk_stream')
    } catch {
      setError('Microphone permission is required.')
    }
  }

  function stop() {
    if (recorder.current?.state === 'recording') recorder.current.stop()
  }

  function cancel() {
    recorder.current?.stop()
    audio.current?.pause()
    audio.current = null
    speechSynthesis.cancel()
    setListening(false)
    setStatus('idle')
  }

  async function clearMemory() {
    await fetch(`${API}/api/memory`, { method: 'DELETE' })
    setHistory([])
  }

  function connectCalendar() {
    window.open(`${API}/api/calendar/auth`, '_blank')
  }

  return {
    API,
    listening,
    transcript,
    partial,
    response,
    history,
    status,
    calendarConnected,
    error,
    start,
    stop,
    cancel,
    clearMemory,
    connectCalendar,
  }
}
