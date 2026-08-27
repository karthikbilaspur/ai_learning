"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { SYSTEM_PROMPTS, type PromptKey } from "@/lib/prompts";

type Conversation = {
  id: string;
  title: string;
  promptKey: PromptKey;
  createdAt: string;
  updatedAt: string;
};

type StoredMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
};

const promptLabels: Record<PromptKey, string> = {
  default: "Default",
  codingExpert: "Coding Expert",
  writer: "Writer",
  teacher: "Teacher",
};

function toUIMessage(message: StoredMessage) {
  return {
    id: message.id,
    role: message.role,
    parts: [{ type: "text" as const, text: message.content }],
  };
}

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [promptKey, setPromptKey] = useState<PromptKey>("default");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loadingConversation, setLoadingConversation] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",
        body: () => ({ conversationId, systemPromptKey: promptKey }),
      }),
    [conversationId, promptKey],
  );

  const { messages, sendMessage, status, error, stop, regenerate, setMessages } = useChat({
    transport,
  });

  const isLoading = status === "streaming" || status === "submitted";

  const loadConversations = useCallback(async () => {
    const response = await fetch("/api/conversations", { cache: "no-store" });
    if (!response.ok) throw new Error("Unable to load conversations");
    const data = await response.json();
    setConversations(data.conversations);
    return data.conversations as Conversation[];
  }, []);

  const createConversation = useCallback(
    async (key: PromptKey = promptKey) => {
      const response = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ promptKey: key }),
      });
      if (!response.ok) throw new Error("Unable to create conversation");
      const data = await response.json();
      const conversation = data.conversation as Conversation;
      setConversations((current) => [conversation, ...current]);
      setConversationId(conversation.id);
      setMessages([]);
      return conversation;
    },
    [promptKey, setMessages],
  );

  const selectConversation = useCallback(
    async (id: string) => {
      if (isLoading) return;
      setLoadingConversation(true);
      try {
        const response = await fetch(`/api/conversations/${id}`, { cache: "no-store" });
        if (!response.ok) throw new Error("Unable to load conversation");
        const data = await response.json();
        setConversationId(id);
        setPromptKey(data.conversation.promptKey as PromptKey);
        setMessages(data.conversation.messages.map(toUIMessage));
      } finally {
        setLoadingConversation(false);
      }
    },
    [isLoading, setMessages],
  );

  useEffect(() => {
    loadConversations()
      .then((items) => {
        if (items.length) {
          void selectConversation(items[0].id);
        } else {
          void createConversation();
        }
      })
      .catch((e) => console.error(e));
  }, [loadConversations]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!input.trim() || isLoading || !conversationId) return;
    sendMessage({ text: input.trim() });
    setInput("");
  };

  const handleNewChat = () => {
    if (!isLoading) void createConversation();
  };

  const deleteConversation = async (id: string) => {
    if (isLoading) return;
    const response = await fetch(`/api/conversations/${id}`, { method: "DELETE" });
    if (!response.ok) return;
    const remaining = conversations.filter((c) => c.id !== id);
    setConversations(remaining);
    if (conversationId === id) {
      if (remaining[0]) await selectConversation(remaining[0].id);
      else await createConversation();
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex">
      {sidebarOpen && (
        <aside className="w-72 border-r border-zinc-800 bg-zinc-950 hidden md:flex flex-col">
          <div className="p-4 border-b border-zinc-800">
            <button
              onClick={handleNewChat}
              className="w-full rounded-xl bg-white text-black py-2.5 font-semibold hover:bg-zinc-200 disabled:opacity-50"
              disabled={isLoading}
            >
              + New chat
            </button>
          </div>
          <div className="p-3 space-y-1 overflow-y-auto flex-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group flex items-center gap-2 rounded-lg ${
                  conversation.id === conversationId ? "bg-zinc-800" : "hover:bg-zinc-900"
                }`}
              >
                <button
                  onClick={() => void selectConversation(conversation.id)}
                  className="flex-1 text-left px-3 py-2.5 text-sm truncate"
                >
                  {conversation.title}
                </button>
                <button
                  onClick={() => void deleteConversation(conversation.id)}
                  className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-300 px-2"
                  aria-label="Delete conversation"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </aside>
      )}

      <main className="min-w-0 flex-1 flex flex-col min-h-screen">
        <header className="border-b border-zinc-800 p-4 flex items-center justify-between sticky top-0 bg-zinc-950/90 backdrop-blur z-10">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="border border-zinc-800 rounded-lg px-2.5 py-1.5 text-sm hover:bg-zinc-900"
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <h1 className="font-bold tracking-tight whitespace-nowrap hidden sm:block">AI Chat</h1>
            <select
              value={promptKey}
              disabled={isLoading}
              onChange={(e) => setPromptKey(e.target.value as PromptKey)}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm"
            >
              {Object.keys(SYSTEM_PROMPTS).map((key) => (
                <option key={key} value={key}>
                  {promptLabels[key as PromptKey]}
                </option>
              ))}
            </select>
          </div>
          <div className="text-xs text-zinc-500 hidden lg:block">
            Persistent history · Streaming · Rate limited
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto p-4 md:p-6 space-y-6">
            {loadingConversation && <div className="text-center text-sm text-zinc-500">Loading conversation…</div>}

            {!loadingConversation && messages.length === 0 && (
              <div className="text-center mt-20 space-y-4">
                <div className="text-4xl">✨</div>
                <h2 className="text-2xl font-semibold">How can I help you today?</h2>
                <div className="grid sm:grid-cols-2 gap-2 max-w-lg mx-auto mt-6">
                  {[
                    "Build a landing page with Tailwind",
                    "Explain RAG in simple terms",
                    "Write a rate limiter in Node",
                    "Debug my streaming response",
                  ].map((question) => (
                    <button
                      key={question}
                      onClick={() => setInput(question)}
                      className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-left hover:bg-zinc-800 transition"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message) => {
              const text = message.parts
                .filter((part) => part.type === "text")
                .map((part) => part.text)
                .join("");

              return (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[88%] rounded-2xl p-4 ${
                      message.role === "user"
                        ? "bg-white text-black"
                        : "bg-zinc-900 border border-zinc-800"
                    }`}
                  >
                    {message.role === "user" ? (
                      <div className="whitespace-pre-wrap">{text}</div>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
                      </div>
                    )}

                    {message.role === "assistant" && !isLoading && (
                      <div className="mt-3 flex gap-3 border-t border-zinc-800 pt-2">
                        <button
                          onClick={() => void navigator.clipboard.writeText(text)}
                          className="text-xs text-zinc-400 hover:text-white"
                        >
                          Copy
                        </button>
                        <button onClick={() => void regenerate()} className="text-xs text-zinc-400 hover:text-white">
                          Regenerate
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {isLoading && (
              <div className="flex gap-2 items-center text-zinc-500 text-sm">
                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                <button
                  onClick={() => stop()}
                  className="ml-3 border border-zinc-700 rounded-full px-3 py-1 text-xs hover:bg-zinc-800"
                >
                  Stop
                </button>
              </div>
            )}

            {error && (
              <div className="bg-red-950/50 border border-red-900 text-red-200 p-3 rounded-xl text-sm">
                {error.message || "Something went wrong. Please try again."}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="border-t border-zinc-800 p-4 sticky bottom-0 bg-zinc-950">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              maxLength={30000}
              disabled={!conversationId || isLoading}
              placeholder="Ask anything…"
              className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-zinc-600 placeholder:text-zinc-600 disabled:opacity-50"
            />
            <button
              disabled={!input.trim() || isLoading || !conversationId}
              className="bg-white text-black px-6 rounded-xl font-semibold disabled:opacity-50 hover:bg-zinc-200 transition"
            >
              Send
            </button>
          </form>
          <div className="max-w-3xl mx-auto text-[11px] text-zinc-600 text-center mt-2">
            Persistent conversations · {promptLabels[promptKey]} · Usage tracked per response
          </div>
        </div>
      </main>
    </div>
  );
}
