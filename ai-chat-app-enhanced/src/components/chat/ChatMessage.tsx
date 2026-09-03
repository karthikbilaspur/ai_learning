"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessageProps = {
  message: {
    id: string;
    role: string;
    parts: Array<{
      type: string;
      text?: string;
    }>;
  };
  isLoading: boolean;
  onRegenerate: () => void;
};

export function ChatMessage({
  message,
  isLoading,
  onRegenerate,
}: ChatMessageProps) {
  const text = message.parts
    .filter(
      (part) => part.type === "text",
    )
    .map((part) => part.text ?? "")
    .join("");

  const isUser =
    message.role === "user";

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`max-w-[88%] rounded-2xl p-4 ${
          isUser
            ? "bg-white text-black"
            : "bg-zinc-900 border border-zinc-800"
        }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap">
            {text}
          </div>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
            >
              {text}
            </ReactMarkdown>
          </div>
        )}

        {message.role === "assistant" &&
          !isLoading && (
            <div className="mt-3 flex gap-3 border-t border-zinc-800 pt-2">
              <button
                onClick={() =>
                  void navigator.clipboard.writeText(
                    text,
                  )
                }
                className="text-xs text-zinc-400 hover:text-white"
              >
                Copy
              </button>

              <button
                onClick={onRegenerate}
                className="text-xs text-zinc-400 hover:text-white"
              >
                Regenerate
              </button>
            </div>
          )}
      </div>
    </div>
  );
}