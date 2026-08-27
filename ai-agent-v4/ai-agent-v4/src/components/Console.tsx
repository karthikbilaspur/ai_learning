import { useState } from "react";
import type { AgentResponse, ChatMessage, PendingCall, Tool, TraceEvent } from "../types";
import { confirmAgent, runAgent } from "../lib/api";
import TraceView from "./TraceView";
import ConfirmBar from "./ConfirmBar";

export default function Console({ tool }: { tool: Tool }) {
  const [input, setInput] = useState(tool.example);
  const [answer, setAnswer] = useState("");
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pendingCall, setPendingCall] = useState<PendingCall | null>(null);

  function handleResponse(d: AgentResponse) {
    setTrace(d.trace || []);
    if (d.needsConfirmation && d.sessionId && d.pendingCall) {
      setSessionId(d.sessionId);
      setPendingCall(d.pendingCall);
      return;
    }
    setSessionId(null);
    setPendingCall(null);
    setAnswer(d.answer || "");
    setHistory((h) => [...h, { role: "user", content: input }, { role: "assistant", content: d.answer || "" }].slice(-12));
  }

  async function run() {
    setBusy(true);
    setError("");
    setAnswer("");
    setTrace([]);
    setPendingCall(null);
    try {
      handleResponse(await runAgent(input, history));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  async function decide(approve: boolean) {
    if (!sessionId) return;
    setBusy(true);
    setError("");
    try {
      handleResponse(await confirmAgent(sessionId, approve));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="console">
      <div className="toolhead">
        <div>
          <span className={"pill " + tool.kind}>{tool.kind}</span>
          <h2>{tool.name}</h2>
          <p>{tool.description}</p>
        </div>
        <span className="status">{busy ? "● Agent running" : "● Ready"}</span>
      </div>

      <textarea value={input} onChange={(e) => setInput(e.target.value)} rows={4} />
      <button onClick={run} disabled={busy || !!pendingCall}>
        {busy ? "Running…" : "Run agent"}
      </button>

      {error && <div className="error-banner">{error}</div>}
      {pendingCall && <ConfirmBar pendingCall={pendingCall} busy={busy} onDecision={decide} />}

      <section>
        <h3>Final response</h3>
        <div className="answer">{answer || "Run a request to see the LLM response."}</div>
      </section>

      <TraceView trace={trace} />
    </div>
  );
}
