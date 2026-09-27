"use client";

import { useState, useRef } from "react";
import { Paperclip, Send, Terminal, FileText, CheckCircle2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolName?: string;
  filePath?: string;
}

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeFile, setActiveFile] = useState<{ name: string; path: string } | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File Upload Handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setActiveFile({ name: data.filename, path: data.file_path });
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
    }
  };

  // Streaming Submit Handler
  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!input.trim() && !activeFile) || loading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      filePath: activeFile?.path,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentPrompt = input;
    const currentFilePath = activeFile?.path;
    
    setInput("");
    setActiveFile(null);
    setLoading(true);

    // Placeholder for assistant's streaming response
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const response = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentPrompt, file_path: currentFilePath }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");

      if (!reader) return;

      let partialLine = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = (partialLine + chunk).split("\n\n");
        partialLine = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const rawData = line.replace("data: ", "").trim();
            if (rawData === "[DONE]") break;

            try {
              const parsed = JSON.parse(rawData);
              
              setMessages((prev) => {
                const newMsgs = [...prev];
                const lastMsg = newMsgs[newMsgs.length - 1];

                if (parsed.type === "token") {
                  lastMsg.content += parsed.content;
                } else if (parsed.type === "tool_call") {
                  lastMsg.toolName = parsed.tool_name;
                }
                return newMsgs;
              });
            } catch (err) {
              console.error("JSON Parsing Error", err);
            }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error connecting to backend stream." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-6 bg-slate-950 text-slate-100">
      <div className="w-full max-w-3xl flex flex-col h-[90vh] bg-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-800">
        
        {/* Header */}
        <header className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between backdrop-blur">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-blue-400" />
            <h1 className="text-md font-semibold text-slate-200">AI Agent Orchestrator Suite</h1>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-blue-950 text-blue-400 border border-blue-800 font-mono">
            Streaming & Tracing Active
          </span>
        </header>

        {/* Message Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-lg p-3.5 text-sm ${
                msg.role === "user" 
                  ? "bg-blue-600 text-white" 
                  : "bg-slate-800 text-slate-200 border border-slate-700/60"
              }`}>
                {msg.toolName && (
                  <div className="flex items-center gap-1.5 text-xs font-mono bg-purple-950/80 text-purple-300 border border-purple-800/80 px-2.5 py-1 rounded mb-2">
                    <span>🛠️ Executing:</span>
                    <span className="font-bold">{msg.toolName}</span>
                  </div>
                )}
                {msg.filePath && (
                  <div className="flex items-center gap-1 text-xs bg-slate-900/60 text-slate-300 p-1.5 rounded mb-2 border border-slate-700">
                    <FileText className="w-3.5 h-3.5 text-blue-400" />
                    <span>Attached: {msg.filePath.split("/").pop()}</span>
                  </div>
                )}
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Active File Indicator */}
        {activeFile && (
          <div className="px-4 py-2 bg-slate-850 border-t border-slate-800 flex items-center justify-between text-xs text-blue-400">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span>Ready for analysis: <strong>{activeFile.name}</strong></span>
            </div>
            <button onClick={() => setActiveFile(null)} className="text-slate-500 hover:text-slate-300">Remove</button>
          </div>
        )}

        {/* Input Bar */}
        <form onSubmit={sendMessage} className="p-4 bg-slate-900/90 border-t border-slate-800 flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={uploading ? "Uploading file..." : "Type a command or process an uploaded file..."}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition"
          />

          <button
            type="submit"
            disabled={loading || uploading}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white font-medium p-2.5 rounded-lg transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

      </div>
    </main>
  );
}