
import { useState } from 'react'
import { useToolCalling } from './hooks/useToolCalling'
import { toolDefinitions } from './tools'

export default function App() {
  const { messages, send, isThinking, logs } = useToolCalling()
  const [input, setInput] = useState('')

  const chips = [
    "Calculate (847*12)/3",
    "Find orders with MacBook",
    "What's our refund policy?",
    "Weather in Bangalore?",
    "Price of Bitcoin?",
    "Search web for React 19 features",
    "Create meeting tomorrow 3pm",
    "Translate hello world to Spanish",
    "Generate QR for my portfolio",
    "What time is it in Tokyo?"
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 360px', height: '100vh', background: '#0a0a0b', color: '#e4e4e7', fontFamily: 'Inter, system-ui' }}>
      {/* Tools */}
      <div style={{ borderRight: '1px solid #27272a', padding: 16, overflowY: 'auto' }}>
        <h2 style={{ fontWeight: 700, marginBottom: 12 }}>🔧 10 Tools Registry</h2>
        {toolDefinitions.map(t => (
          <div key={t.name} style={{ background: '#18181b', border: '1px solid #27272a', borderRadius: 12, padding: 12, marginBottom: 8 }}>
            <div style={{ fontFamily: 'monospace', fontSize: 13, color: '#a1a1ff', fontWeight: 700 }}>{t.name}</div>
            <div style={{ fontSize: 12, color: '#a1a1aa', marginTop: 4 }}>{t.description}</div>
          </div>
        ))}
        <div style={{ marginTop: 16, fontSize: 12, color: '#71717a' }}>
          Flow: User → LLM → Tool Decision → JS/API → LLM → Response
        </div>
      </div>

      {/* Chat */}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #27272a', fontWeight: 700 }}>AI Assistant • Tool Calling Demo (React/TS)</div>
        <div style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {messages.length === 0 && <div style={{ color: '#71717a' }}>Start with an example below 👇</div>}
          {messages.map(m => (
            <div key={m.id} style={{ background: m.role === 'user' ? '#27272a' : '#18181b', padding: 14, borderRadius: 14, border: '1px solid #27272a', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
              <div style={{ fontSize: 11, color: '#71717a', marginBottom: 4 }}>{m.role}</div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: 14, lineHeight: 1.5 }}>{m.content}</div>
              {m.toolCalls && (
                <pre style={{ marginTop: 10, background: '#0a0a0b', padding: 10, borderRadius: 8, fontSize: 11, overflowX: 'auto', border: '1px solid #3f3f46' }}>
                  {JSON.stringify(m.toolCalls, null, 2)}
                </pre>
              )}
            </div>
          ))}
          {isThinking && <div style={{ color: '#a1a1ff' }}>● LLM thinking → deciding tool → executing...</div>}
        </div>

        <div style={{ padding: 12, borderTop: '1px solid #27272a' }}>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
            {chips.map(c => (
              <button key={c} onClick={() => { setInput(c); send(c) }} style={{ fontSize: 11, background: '#18181b', border: '1px solid #27272a', color: '#d4d4d8', borderRadius: 20, padding: '6px 10px', cursor: 'pointer' }}>{c}</button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && (send(input), setInput(''))} placeholder="Ask anything... try math, weather, orders" style={{ flex: 1, background: '#18181b', border: '1px solid #27272a', borderRadius: 10, padding: '10px 14px', color: 'white' }} />
            <button onClick={() => { send(input); setInput('') }} style={{ background: 'white', color: 'black', borderRadius: 10, padding: '10px 16px', fontWeight: 700, cursor: 'pointer' }}>Send</button>
          </div>
        </div>
      </div>

      {/* Logs */}
      <div style={{ borderLeft: '1px solid #27272a', padding: 16, overflowY: 'auto', background: '#09090b' }}>
        <h3 style={{ fontWeight: 700, marginBottom: 12 }}>Execution Log</h3>
        {logs.length === 0 && <div style={{ color: '#52525b', fontSize: 12 }}>No tools executed yet</div>}
        {logs.map(l => (
          <div key={l.id} style={{ background: '#18181b', border: '1px solid #27272a', borderRadius: 10, padding: 10, marginBottom: 10 }}>
            <div style={{ fontSize: 12, fontFamily: 'monospace', color: '#22c55e' }}>✓ {l.tool} ({l.latency}ms)</div>
            <pre style={{ fontSize: 10, marginTop: 6, whiteSpace: 'pre-wrap', color: '#a1a1aa' }}>{JSON.stringify(l.result, null, 2).slice(0, 400)}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
