import VoiceConsole from './components/VoiceConsole.jsx'
import MemoryPanel from './components/MemoryPanel.jsx'
import { useJarvis } from './useJarvis.js'

export default function App() {
  const jarvis = useJarvis()

  return (
    <main>
      <header>
        <div>
          <div className="eyebrow">LOCAL AI SYSTEM</div>
          <h1>
            JARVIS <span>Lite</span>
          </h1>
          <p>Private voice assistant · Whisper · Ollama · Piper · Google Calendar</p>
        </div>
        <div className={`pill ${jarvis.status}`}>● {jarvis.status}</div>
      </header>

      <section className="grid">
        <VoiceConsole
          status={jarvis.status}
          listening={jarvis.listening}
          partial={jarvis.partial}
          transcript={jarvis.transcript}
          response={jarvis.response}
          error={jarvis.error}
          calendarConnected={jarvis.calendarConnected}
          onConnectCalendar={jarvis.connectCalendar}
          onStart={jarvis.start}
          onStop={jarvis.stop}
          onCancel={jarvis.cancel}
        />
        <MemoryPanel history={jarvis.history} onClear={jarvis.clearMemory} />
      </section>

      <footer>Built with a modular React + Node.js + Python architecture. Local inference by default.</footer>
    </main>
  )
}
