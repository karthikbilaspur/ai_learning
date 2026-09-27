"use client";

import type { Conversation } from "../chat/ChatPage";
import { ConversationItem } from "./ConversationItem";

type ConversationSidebarProps = {
  conversations: Conversation[];
  conversationId: string | null;
  open: boolean;
  disabled: boolean;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
};

export function ConversationSidebar({
  conversations,
  conversationId,
  open,
  disabled,
  onNewChat,
  onSelect,
  onDelete,
}: ConversationSidebarProps) {
  if (!open) {
    return null;
  }

  return (
    <aside className="w-72 border-r border-zinc-800 bg-zinc-950 hidden md:flex flex-col">
      <div className="p-4 border-b border-zinc-800">
        <button
          onClick={onNewChat}
          disabled={disabled}
          className="w-full rounded-xl bg-white text-black py-2.5 font-semibold hover:bg-zinc-200 disabled:opacity-50"
        >
          + New chat
        </button>
      </div>

      <div className="p-3 space-y-1 overflow-y-auto flex-1">
        {conversations.map(
          (conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              selected={
                conversation.id ===
                conversationId
              }
              disabled={disabled}
              onSelect={() =>
                onSelect(
                  conversation.id,
                )
              }
              onDelete={() =>
                onDelete(
                  conversation.id,
                )
              }
            />
          ),
        )}
      </div>
    </aside>
  );
}