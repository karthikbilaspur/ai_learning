import type { TraceEvent } from "../types";

export default function TraceView({ trace }: { trace: TraceEvent[] }) {
  return (
    <section>
      <div className="tracehead">
        <h3>Execution trace</h3>
        <small>Private reasoning is not displayed.</small>
      </div>
      {trace.length ? (
        trace.map((x, i) => (
          <div className="event" key={i}>
            <b>
              {x.type === "tool_call" ? "🔧 TOOL CALL" : "✓ TOOL RESULT"} — {x.name}
            </b>
            <small> round {x.round}</small>
            <pre>{JSON.stringify(x.type === "tool_call" ? x.args : x.result, null, 2)}</pre>
          </div>
        ))
      ) : (
        <p className="muted">Tool calls will appear here.</p>
      )}
    </section>
  );
}
