import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import FileViewer from './components/FileViewer.jsx'
import GraphView from './components/GraphView.jsx'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [repoUrl, setRepoUrl] = useState('https://github.com/facebook/react')
  const [repos, setRepos] = useState([])
  const [activeRepo, setActiveRepo] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [citations, setCitations] = useState([])
  const [graph, setGraph] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [ingesting, setIngesting] = useState(false)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState('')

  const activeRepoMeta = repos.find((r) => r.repo_id === activeRepo)

  const ingest = async () => {
    setIngesting(true)
    setError('')
    try {
      const res = await axios.post(`${API}/ingest`, { repo_url: repoUrl })
      setRepos((prev) => [...prev, res.data])
      setActiveRepo(res.data.repo_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to ingest repo. Check the URL is a public https:// GitHub/GitLab/Bitbucket link.')
    } finally {
      setIngesting(false)
    }
  }

  const ask = async () => {
    if (!activeRepo || !question.trim() || asking) return

    setAsking(true)
    setError('')
    setAnswer('')
    setCitations([])
    setGraph(null)

    try {
      const res = await fetch(`${API}/query/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_id: activeRepo, question }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `HTTP ${res.status}`)
      }

      const reader = res.body.getReader()
      let full = ''
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += new TextDecoder().decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // keep the possibly-incomplete last line for next chunk

        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          try {
            const data = JSON.parse(line.slice(5))
            if (data.token) {
              full += data.token
              setAnswer(full)
            }
            if (data.citations) setCitations(data.citations)
            if (data.graph) setGraph(data.graph)
          } catch {
            // ignore partial/malformed SSE frames
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Query failed.')
    } finally {
      setAsking(false)
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: 320, borderRight: '1px solid #25253a', padding: 16, overflowY: 'auto' }}>
        <h2>Repos</h2>
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          style={{ width: '100%', padding: 8, background: '#0a0a0f', color: 'white', border: '1px solid #333' }}
        />
        <button className="btn" style={{ marginTop: 8, width: '100%' }} onClick={ingest} disabled={ingesting}>
          {ingesting ? 'Indexing with AST...' : 'Ingest Repo'}
        </button>

        <div style={{ marginTop: 16 }}>
          {repos.map((r) => (
            <div
              key={r.repo_id}
              onClick={() => setActiveRepo(r.repo_id)}
              style={{
                padding: 8,
                background: activeRepo === r.repo_id ? '#25253a' : 'transparent',
                borderRadius: 8,
                cursor: 'pointer',
                marginBottom: 4,
              }}
            >
              <b>{r.name}</b>
              <br />
              <small>
                {r.files} files, {r.chunks} AST chunks, {r.call_graph_edges} call edges
              </small>
            </div>
          ))}
        </div>

        {activeRepoMeta && (
          <div style={{ marginTop: 20 }}>
            <h4>Indexed</h4>
            <small style={{ opacity: 0.7 }}>
              ✅ AST chunking
              <br />
              ✅ Hybrid BM25 + Vector
              <br />
              ✅ Cross-encoder rerank
              <br />
              {activeRepoMeta.call_graph_edges > 0 ? '✅' : '⚠️'} Call graph ({activeRepoMeta.call_graph_edges} edges,
              name-matched)
              <br />
              ✅ Bounded agentic loop (up to 2 extra file reads)
            </small>
          </div>
        )}
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #25253a', display: 'flex', gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && ask()}
            placeholder="Ask: How does reconciliation work? What breaks if I change useState?"
            style={{ flex: 1, padding: 12, background: '#15151f', border: '1px solid #333', color: 'white', borderRadius: 8 }}
          />
          <button className="btn" onClick={ask} disabled={!activeRepo || asking}>
            {asking ? 'Thinking...' : 'Ask'}
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
          {!activeRepo && <div style={{ opacity: 0.5 }}>Ingest a repo on the left to get started.</div>}
          {error && <div style={{ color: '#f87171', marginBottom: 12 }}>{error}</div>}

          {answer && (
            <div className="card">
              <div className="markdown-body">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
              <div style={{ marginTop: 12, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {citations.map((c, i) => (
                  <span key={i} className="citation" onClick={() => setSelectedFile(c)}>
                    {c.file}:{c.line} ({c.type}) score:{c.score?.toFixed(2)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {graph && (
            <div className="card" style={{ marginTop: 16 }}>
              <h4>Call Graph</h4>
              <GraphView graph={graph} />
            </div>
          )}
        </div>
      </div>

      <div style={{ width: 420, borderLeft: '1px solid #25253a', display: selectedFile ? 'block' : 'none' }}>
        {selectedFile && <FileViewer repoId={activeRepo} file={selectedFile} onClose={() => setSelectedFile(null)} />}
      </div>
    </div>
  )
}
