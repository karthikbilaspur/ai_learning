import React, { useState } from 'react';

export default function ResearchForm({ onStart, loading }) {
  const [company, setCompany] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (company.trim()) onStart(company);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-4 bg-slate-800 p-4 rounded-xl border border-slate-700">
      <input
        type="text"
        placeholder="Enter company name (e.g., Stripe, Notion)..."
        value={company}
        onChange={(e) => setCompany(e.target.value)}
        disabled={loading}
        className="flex-1 bg-slate-900 px-4 py-2 rounded-lg border border-slate-700 text-white focus:outline-none focus:border-blue-500"
      />
      <button
        type="submit"
        disabled={loading || !company.trim()}
        className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white font-medium px-6 py-2 rounded-lg transition-colors"
      >
        {loading ? 'Analyzing...' : 'Run Agent'}
      </button>
    </form>
  );
}