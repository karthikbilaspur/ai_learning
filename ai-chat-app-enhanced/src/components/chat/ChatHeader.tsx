"use client";

import {
  SYSTEM_PROMPTS,
  type PromptKey,
} from "@/lib/prompts";

const promptLabels: Record<
  PromptKey,
  string
> = {
  default: "Default",
  codingExpert: "Coding Expert",
  writer: "Writer",
  teacher: "Teacher",
};

type ChatHeaderProps = {
  promptKey: PromptKey;
  disabled: boolean;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  onPromptChange: (
    key: PromptKey,
  ) => void;
};

export function ChatHeader({
  promptKey,
  disabled,
  onToggleSidebar,
  onPromptChange,
}: ChatHeaderProps) {
  return (
    <header className="border-b border-zinc-800 p-4 flex items-center justify-between sticky top-0 bg-zinc-950/90 backdrop-blur z-10">
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="border border-zinc-800 rounded-lg px-2.5 py-1.5 text-sm hover:bg-zinc-900"
          aria-label="Toggle sidebar"
        >
          ☰
        </button>

        <h1 className="font-bold tracking-tight whitespace-nowrap hidden sm:block">
          AI Chat
        </h1>

        <select
          value={promptKey}
          disabled={disabled}
          onChange={(event) =>
            onPromptChange(
              event.target.value as PromptKey,
            )
          }
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm"
        >
          {Object.keys(SYSTEM_PROMPTS).map(
            (key) => (
              <option
                key={key}
                value={key}
              >
                {
                  promptLabels[
                    key as PromptKey
                  ]
                }
              </option>
            ),
          )}
        </select>
      </div>

      <div className="text-xs text-zinc-500 hidden lg:block">
        Persistent history · Streaming · Rate limited
      </div>
    </header>
  );
}