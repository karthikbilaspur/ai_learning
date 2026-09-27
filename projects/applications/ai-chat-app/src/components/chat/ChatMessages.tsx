"use client";

import { RefObject } from "react";

import { ChatMessage } from "./ChatMessage";
import { ChatEmptyState } from "./ChatEmptyState";
import { ChatLoading } from "./ChatLoading";

type ChatMessagesProps = {
  messages: Array<{
    id: string;
    role: string;
    parts: Array<{
      type: string;
      text?: string;
    }>;
  }>;

  isLoading: boolean;

  loadingConversation: boolean;

  error: Error | undefined;

  onRegenerate: () => void;

  onStop: () => void;

  bottomRef: RefObject<HTMLDivElement | null>;

  onQuestionSelect: (
    question: string,
  ) => void;
};

export function ChatMessages({
  messages,
  isLoading,
  loadingConversation,
  error,
  onRegenerate,
  onStop,
  bottomRef,
  onQuestionSelect,
}: ChatMessagesProps) {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto p-4 md:p-6 space-y-6">
        {loadingConversation && (
          <div className="text-center text-sm text-zinc-500">
            Loading conversation…
          </div>
        )}

        {!loadingConversation &&
          messages.length === 0 && (
            <ChatEmptyState
              onQuestionSelect={
                onQuestionSelect
              }
            />
          )}

        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            isLoading={isLoading}
            onRegenerate={
              onRegenerate
            }
          />
        ))}

        {isLoading && (
          <ChatLoading
            onStop={onStop}
          />
        )}

        {error && (
          <div className="bg-red-950/50 border border-red-900 text-red-200 p-3 rounded-xl text-sm">
            {error.message ||
              "Something went wrong. Please try again."}
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}