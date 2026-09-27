import React from 'react';

export default function AgentLogStream({ currentNode, logs, loading }) {
  return (
    <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-700 pb-2">
        <span className="text-sm font-semibold text-slate-300">Live Execution Logs</span>
        {loading && (
          <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-1 rounded">
            {currentNode}
          </span>
        )}
      </div>
      <div className="font-mono text-xs text-slate-400 space-y-1 max-h-40 overflow-y-auto">
        {logs.map((log, index) => (
          <div key={index} className="text-emerald-400">{log}</div>
        ))}
      </div>
    </div>
  );
}