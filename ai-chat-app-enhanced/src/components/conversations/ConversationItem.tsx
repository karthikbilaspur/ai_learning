"use client";

import type { Conversation } from "../chat/ChatPage";

type ConversationItemProps = {
  conversation: Conversation;
  selected: boolean;
  disabled: boolean;
  onSelect: () => void;
  onDelete: () => void;
};

export function ConversationItem({
  conversation,
  selected,
  disabled,
  onSelect,
  onDelete,
}: ConversationItemProps) {
  return (
    <div
      className={`group flex items-center gap-2 rounded-lg ${
        selected
          ? "bg-zinc-800"
          : "hover:bg-zinc-900"
      }`}
    >
      <button
        onClick={onSelect}
        disabled={disabled}
        className="flex-1 text-left px-3 py-2.5 text-sm truncate disabled:opacity-50"
      >
        {conversation.title}
      </button>

      <button
        onClick={onDelete}
        disabled={disabled}
        className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-300 px-2 disabled:opacity-50"
        aria-label="Delete conversation"
      >
        ×
      </button>
    </div>
  );
}