import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Download } from 'lucide-react';

export default function ReportViewer({ companyName, report }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const response = await fetch('/api/research/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, markdown_content: report }),
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${companyName}_Market_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error("PDF export failed:", err);
    }
    setDownloading(false);
  };

  return (
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4">
      <div className="flex justify-between items-center border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-white">Synthesized Market Report</h2>
        <button
          onClick={handleDownloadPDF}
          disabled={downloading}
          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3 py-1.5 rounded transition-colors"
        >
          <Download size={14} />
          {downloading ? 'Generating PDF...' : 'Download PDF'}
        </button>
      </div>
      <div className="prose prose-invert max-w-none text-slate-300 text-sm">
        <ReactMarkdown>{report}</ReactMarkdown>
      </div>
    </div>
  );
}