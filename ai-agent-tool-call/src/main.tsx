import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Tool = {
  name: string;
  title: string;
  description: string;
  example: string;
};

const toolList: Tool[] = [
  { name: "calculate", title: "Calculator", description: "Runs arithmetic dynamically.", example: "Calculate (783 * 42) / 6" },
  { name: "search_dataset", title: "Dataset Search", description: "Searches the demo employee dataset.", example: "Find engineers in Bengaluru" },
  { name: "analyze_dataset", title: "Data Analysis", description: "Computes live statistics from the dataset.", example: "What is the average engineering salary?" },
  { name: "get_weather", title: "Weather API", description: "Calls Open-Meteo for live weather.", example: "What's the weather in Bengaluru?" },
  { name: "convert_currency", title: "Currency API", description: "Converts currencies using live rates.", example: "Convert 50000 INR to USD" },
  { name: "get_time", title: "Time Tool", description: "Gets current time for an IANA timezone.", example: "What time is it in Asia/Kolkata?" },
  { name: "search_web", title: "Web Search", description: "Uses a web search API for current topics.", example: "Search the web for TypeScript" },
  { name: "lookup_products", title: "Product Lookup", description: "Searches the local product catalog.", example: "Find laptops under 80000" },
  { name: "create_task", title: "Task Action", description: "Creates a task as an actual agent action.", example: "Create a high priority task to review the demo" }
];

function App() {
  const [selected, setSelected] = useState(toolList[0]);
  const [message, setMessage] = useState(toolList[0].example);
  const [answer, setAnswer] = useState("");
  const [trace, setTrace] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    setAnswer("");
    setTrace([]);
    try {
      const r = await fetch("http://localhost:3001/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "Request failed");
      setAnswer(data.answer);
      setTrace(data.trace || []);
    } catch (e) {
      setAnswer(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <div>
          <span className="eyebrow">REACT + TYPESCRIPT + LLM</span>
          <h1>AI Agent Tool Calling Lab</h1>
          <p>Pick a tool page, give the agent a goal, and watch the LLM → tool → result → LLM loop.</p>
        </div>
        <div className="badge">Agent demo</div>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <h2>Tools</h2>
          {toolList.map(tool => (
            <button
              key={tool.name}
              className={selected.name === tool.name ? "tool active" : "tool"}
              onClick={() => { setSelected(tool); setMessage(tool.example); }}
            >
              <strong>{tool.title}</strong>
              <small>{tool.name}</small>
            </button>
          ))}
        </aside>

        <main>
          <section className="hero-card">
            <span className="pill">{selected.name}</span>
            <h2>{selected.title}</h2>
            <p>{selected.description}</p>
            <textarea value={message} onChange={e => setMessage(e.target.value)} rows={4} />
            <button className="run" onClick={run} disabled={loading}>
              {loading ? "Agent is running..." : "Run agent"}
            </button>
          </section>

          <section className="answer">
            <h3>Final response</h3>
            <div className="response">{answer || "Run a request to see the LLM response."}</div>
          </section>

          <section className="trace">
            <h3>Agent trace</h3>
            {trace.length === 0 && <p className="muted">Tool calls and tool results will appear here.</p>}
            {trace.map((item, i) => (
              <div className="trace-row" key={i}>
                <div className="trace-label">{item.type === "tool_call" ? "🔧 TOOL CALL" : "✓ TOOL RESULT"} <b>{item.name}</b></div>
                <pre>{JSON.stringify(item.type === "tool_call" ? item.args : item.result, null, 2)}</pre>
              </div>
            ))}
          </section>
        </main>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);