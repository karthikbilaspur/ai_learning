"use client";

import type React from "react";
import type { PromptKey } from "@/lib/prompts";

const promptLabels: Record<
  PromptKey,
  string
> = {
  default: "Default",
  codingExpert: "Coding Expert",
  writer: "Writer",
  teacher: "Teacher",
};

type ChatInputProps = {
  input: string;
  disabled: boolean;
  isLoading: boolean;
  promptKey: PromptKey;
  onInputChange: (
    value: string,
  ) => void;
  onSubmit: (
    event: React.FormEvent<HTMLFormElement>,
  ) => void;
};

export function ChatInput({
  input,
  disabled,
  isLoading,
  promptKey,
  onInputChange,
  onSubmit,
}: ChatInputProps) {
  return (
    <div className="border-t border-zinc-800 p-4 sticky bottom-0 bg-zinc-950">
      <form
        onSubmit={onSubmit}
        className="max-w-3xl mx-auto flex gap-2"
      >
        <input
          value={input}
          onChange={(event) =>
            onInputChange(
              event.target.value,
            )
          }
          maxLength={30000}
          disabled={disabled}
          placeholder="Ask anything…"
          className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-zinc-600 placeholder:text-zinc-600 disabled:opacity-50"
        />

        <button
          disabled={
            !input.trim() ||
            isLoading ||
            disabled
          }
          className="bg-white text-black px-6 rounded-xl font-semibold disabled:opacity-50 hover:bg-zinc-200 transition"
        >
          Send
        </button>
      </form>

      <div className="max-w-3xl mx-auto text-[11px] text-zinc-600 text-center mt-2">
        Persistent conversations ·{" "}
        {promptLabels[promptKey]} · Usage tracked
        per response
      </div>
    </div>
  );
}