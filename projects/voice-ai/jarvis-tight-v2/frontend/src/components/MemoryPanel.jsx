export default function MemoryPanel({ history, onClear }) {
  const recentFirst = history.slice().reverse()

  return (
    <aside className="card memory">
      <div className="top">
        <div>
          <b>Session memory</b>
          <small>{history.length} recent turns</small>
        </div>
        <button onClick={onClear}>Clear</button>
      </div>

      {recentFirst.length === 0 ? (
        <div className="empty">No conversations yet.</div>
      ) : (
        recentFirst.map((turn, i) => (
          <div className="turn" key={i}>
            <div>👤 {turn.user}</div>
            <div>🤖 {turn.ai}</div>
            {turn.tool && <small>tool · {turn.tool}</small>}
          </div>
        ))
      )}
    </aside>
  )
}
