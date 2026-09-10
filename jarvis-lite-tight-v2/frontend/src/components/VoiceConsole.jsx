import Visualizer from './Visualizer.jsx'

export default function VoiceConsole({
  status,
  listening,
  partial,
  transcript,
  response,
  error,
  calendarConnected,
  onConnectCalendar,
  onStart,
  onStop,
  onCancel,
}) {
  return (
    <div className="card hero">
      <div className="top">
        <div>
          <b>Voice console</b>
          <small>{calendarConnected ? 'Calendar connected' : 'Calendar not connected'}</small>
        </div>
        <button onClick={onConnectCalendar}>
          {calendarConnected ? 'Reconnect calendar' : 'Connect calendar'}
        </button>
      </div>

      <Visualizer active={status === 'listening'} />

      <div className="transcript">
        {partial && <span className="partial">{partial}</span>}
        {transcript && (
          <div>
            <b>You</b>
            {transcript}
          </div>
        )}
        {response && (
          <div>
            <b>JARVIS</b>
            {response}
          </div>
        )}
        {error && <div className="error">{error}</div>}
      </div>

      <div className="controls">
        <button
          className={`talk ${listening ? 'active' : ''}`}
          onMouseDown={onStart}
          onMouseUp={onStop}
          onTouchStart={onStart}
          onTouchEnd={onStop}
        >
          {listening ? 'Release to send' : 'Hold to talk'}
        </button>
        <button className="secondary" onClick={onCancel}>
          Stop
        </button>
      </div>

      <div className="hint">Tip: say "what's on my calendar today" or use the LLM for general questions.</div>
    </div>
  )
}
