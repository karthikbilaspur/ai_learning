import { useEffect, useState } from 'react';

export default function ResearchHistory({ onSelectRun }) {
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/research/history');
      const data = await res.json();
      setHistory(data);
    } catch (e) {
      console.error("Failed to load research history", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  if (history.length === 0) return null;

  return (
    <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">Past Research Runs</h3>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {history.map((run) => (
          <button
            key={run.id}
            onClick={() => onSelectRun(run)}
            className="bg-slate-900 border border-slate-700 hover:border-blue-500 text-xs text-slate-300 px-3 py-2 rounded-lg text-left whitespace-nowrap"
          >
            <div className="font-bold text-white">{run.company_name}</div>
            <div className="text-[10px] text-slate-500">
              {new Date(run.created_at).toLocaleDateString()}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}