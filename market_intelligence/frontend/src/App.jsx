import { useState } from 'react';
import ResearchForm from './components/ResearchForm';
import AgentLogStream from './components/AgentLogStream';
import ReportViewer from './components/ReportViewer';
import ResearchHistory from './components/ResearchHistory';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [currentNode, setCurrentNode] = useState('');
  const [company, setCompany] = useState('');
  const [report, setReport] = useState('');

  const handleStartResearch = async (companyName) => {
    setLoading(true);
    setCompany(companyName);
    setLogs([]);
    setCurrentNode('Initializing Workflow...');
    setReport('');

    const response = await fetch('/api/research/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: companyName }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.replace('data: ', ''));
            const { node, update } = data;

            setCurrentNode(`Active Agent: ${node.toUpperCase()}`);
            setLogs((prev) => [...prev, `✓ Executed node: ${node}`]);

            if (update.final_report) {
              setReport(update.final_report);
            }
          } catch (e) {
            console.error("Error parsing SSE chunk:", e);
          }
        }
      }
    }

    setLoading(false);
    setCurrentNode('Completed');
  };

  const handleSelectHistoryRun = (run) => {
    setCompany(run.company_name);
    setReport(run.final_report);
    setLogs([`Loaded past research run from ${new Date(run.created_at).toLocaleDateString()}`]);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 flex flex-col items-center">
      <header className="max-w-4xl w-full mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-400 mb-2">Market Intelligence Agent</h1>
        <p className="text-slate-400">Multi-agent research with Firecrawl, SQLite, and PDF export</p>
      </header>

      <main className="max-w-4xl w-full space-y-6">
        <ResearchForm onStart={handleStartResearch} loading={loading} />
        <ResearchHistory onSelectRun={handleSelectHistoryRun} />
        
        {(loading || logs.length > 0) && (
          <AgentLogStream currentNode={currentNode} logs={logs} loading={loading} />
        )}

        {report && <ReportViewer companyName={company} report={report} />}
      </main>
    </div>
  );
}