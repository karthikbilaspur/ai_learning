import { useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function languageFor(path) {
  if (path.endsWith('.py')) return 'python'
  if (path.endsWith('.ts') || path.endsWith('.tsx')) return 'typescript'
  if (path.endsWith('.md')) return 'markdown'
  return 'javascript'
}

export default function FileViewer({ repoId, file, onClose }) {
  const [content, setContent] = useState('')
  const [status, setStatus] = useState('loading') // loading | ready | error

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    setContent('')

    fetch(`${API}/read-file?repo_id=${encodeURIComponent(repoId)}&path=${encodeURIComponent(file.file)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => {
        if (cancelled) return
        setContent(data.content)
        setStatus('ready')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })

    return () => {
      cancelled = true
    }
  }, [repoId, file.file])

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <b>
          {file.file}:{file.line}
        </b>
        <button onClick={onClose}>X</button>
      </div>
      {status === 'error' ? (
        <div style={{ padding: 16, color: '#f87171' }}>Could not load this file.</div>
      ) : (
        <Editor
          height="90%"
          language={languageFor(file.file)}
          value={status === 'loading' ? '// loading...' : content}
          options={{ readOnly: true, minimap: { enabled: false } }}
        />
      )}
    </div>
  )
}
