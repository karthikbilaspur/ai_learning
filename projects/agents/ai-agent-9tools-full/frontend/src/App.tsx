import { useState } from 'react'

type Msg = { role: 'user' | 'assistant', content: string }

export default function App() {
  const [input, setInput] = useState('')
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [loading, setLoading] = useState(false)

  async function onSend(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg: Msg = { role: 'user', content: input }
    const newHistory = [...msgs, userMsg]
    setMsgs(newHistory)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('http://localhost:4000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newHistory })
      })
      
      if (!res.body) throw new Error('No body')
      
      // Read streaming response
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let assistantText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        // Vercel AI SDK streams as data stream, we just append
        assistantText += chunk
        setMsgs([...newHistory, { role: 'assistant', content: assistantText }])
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err)
      setMsgs([...newHistory, { role: 'assistant', content: `❌ Error: Backend not running? Start it: cd backend && npm run dev\n${errorMessage}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: 24, fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>🤖 AI Agent — 9 Tools</h1>
      <div style={{ color: '#666', marginBottom: 20, fontSize: 14 }}>
        Tools: calculator | web_search | code_executor | file_reader | weather | calendar | database_query | image_generator | memory
      </div>

      <div style={{ border: '1px solid #e5e7eb', borderRadius: 16, minHeight: 480, padding: 16, background: 'white', overflowY: 'auto' }}>
        {msgs.length === 0 && <div style={{ color: '#aaa', marginTop: 180, textAlign: 'center' }}>Ask: "Calculate 25*48 using calculator" or "Search latest AI news"</div>}
        {msgs.map((m, i) => (
          <div key={i} style={{ marginBottom: 14, display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ 
              maxWidth: '80%', 
              padding: '10px 14px', 
              borderRadius: 16, 
              background: m.role === 'user' ? '#111' : '#f3f4f6', 
              color: m.role === 'user' ? '#fff' : '#111',
              whiteSpace: 'pre-wrap',
              fontSize: 14
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && <div style={{ fontSize: 13, color: '#888' }}>Agent thinking + calling tools...</div>}
      </div>

      <form onSubmit={onSend} style={{ display: 'flex', gap: 10, marginTop: 16 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: '14px 16px', borderRadius: 12, border: '1px solid #d1d5db', fontSize: 15 }}
        />
        <button disabled={loading} style={{ padding: '14px 22px', borderRadius: 12, background: '#111', color: 'white', border: 0, fontWeight: 600, cursor: 'pointer' }}>
          Send
        </button>
      </form>
    </div>
  )
}