'use client';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { useState } from 'react';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, status, error } = useChat({
    transport: new DefaultChatTransport({ api: '/api/chat' }),
  });

  const isLoading = status === 'streaming' || status === 'submitted';

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <div className="max-w-3xl mx-auto flex flex-col h-screen">
        <header className="p-4 border-b border-zinc-800 flex justify-between">
          <h1 className="font-bold">AI Chat - Next 16</h1>
          <button onClick={() => localStorage.clear()} className="text-xs text-zinc-400">Clear History</button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map(m => (
            <div key={m.id} className={`p-3 rounded-xl max-w-[85%] ${m.role === 'user'? 'bg-white text-black ml-auto' : 'bg-zinc-900'}`}>
              {m.parts.map((p, i) => p.type === 'text'? <div key={i} className="whitespace-pre-wrap">{p.text}</div> : null)}
            </div>
          ))}
          {isLoading && <div className="text-zinc-500 text-sm animate-pulse">● ● ●</div>}
          {error && <div className="bg-red-950 text-red-200 p-3 rounded">{error.message}</div>}
        </div>

        <form onSubmit={e => {
          e.preventDefault();
          if (!input.trim() || isLoading) return;
          sendMessage({ text: input });
          setInput('');
        }} className="p-4 border-t border-zinc-800 flex gap-2">
          <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask anything..." className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 outline-none focus:border-zinc-700" />
          <button className="bg-white text-black px-6 rounded-lg font-semibold">Send</button>
        </form>
      </div>
    </div>
  );
}