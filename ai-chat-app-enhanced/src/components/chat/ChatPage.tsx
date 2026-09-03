
"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import type { PromptKey } from "@/lib/prompts";

import { useConversations } from "@/hooks/useConversations";
import { useChatConversation } from "@/hooks/useChatConversation";

import { ChatHeader } from "./ChatHeader";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { ConversationSidebar } from "../conversations/ConversationSidebar";

type StoredMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
};

function toUIMessage(message: StoredMessage) {
  return {
    id: message.id,
    role: message.role,
    parts: [
      {
        type: "text" as const,
        text: message.content,
      },
    ],
  };
}

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [promptKey, setPromptKey] =
    useState<PromptKey>("default");

  const [sidebarOpen, setSidebarOpen] =
    useState(true);

  const [
    loadingConversation,
    setLoadingConversation,
  ] = useState(false);

  const bottomRef =
    useRef<HTMLDivElement>(null);

  // ----------------------------------------
  // Conversations
  // ----------------------------------------

  const {
    conversations,
    conversationId,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
  } = useConversations();

  // ----------------------------------------
  // Chat
  // ----------------------------------------

  const {
    messages,
    sendMessage,
    error,
    stop,
    regenerate,
    setMessages,
    isLoading,
  } = useChatConversation({
    conversationId,
    promptKey,
  });

  // ----------------------------------------
  // Initial conversation loading
  // ----------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function initializeChat() {
      try {
        const items =
          await loadConversations();

        if (cancelled) return;

        // No conversations yet.
        if (items.length === 0) {
          await createConversation(
            promptKey,
          );

          return;
        }

        // Load the most recent conversation.
        const conversation =
          await selectConversation(
            items[0].id,
          );

        if (cancelled) return;

        setPromptKey(
          conversation.promptKey,
        );

        setMessages(
          conversation.messages.map(
            toUIMessage,
          ),
        );
      } catch (error) {
        if (!cancelled) {
          console.error(
            "Failed to initialize chat:",
            error,
          );
        }
      }
    }

    void initializeChat();

    return () => {
      cancelled = true;
    };
  }, [
    loadConversations,
    createConversation,
    selectConversation,
    setMessages,
  ]);

  // ----------------------------------------
  // Auto-scroll
  // ----------------------------------------

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // ----------------------------------------
  // Select conversation
  // ----------------------------------------

  const handleSelectConversation =
    async (id: string) => {
      if (isLoading) return;

      setLoadingConversation(true);

      try {
        const conversation =
          await selectConversation(id);

        setPromptKey(
          conversation.promptKey,
        );

        setMessages(
          conversation.messages.map(
            toUIMessage,
          ),
        );
      } catch (error) {
        console.error(
          "Failed to select conversation:",
          error,
        );
      } finally {
        setLoadingConversation(false);
      }
    };

  // ----------------------------------------
  // Send message
  // ----------------------------------------

  const handleSubmit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    const trimmedInput =
      input.trim();

    if (
      !trimmedInput ||
      isLoading ||
      !conversationId
    ) {
      return;
    }

    sendMessage({
      text: trimmedInput,
    });

    setInput("");
  };

  // ----------------------------------------
  // New conversation
  // ----------------------------------------

  const handleNewChat = async () => {
    if (isLoading) return;

    try {
      await createConversation(
        promptKey,
      );

      setMessages([]);
      setInput("");
    } catch (error) {
      console.error(
        "Failed to create conversation:",
        error,
      );
    }
  };

  // ----------------------------------------
  // Delete conversation
  // ----------------------------------------

  const handleDeleteConversation =
    async (id: string) => {
      if (isLoading) return;

      try {
        await deleteConversation(id);

        /*
         * If the deleted conversation wasn't
         * the active one, there is nothing else
         * to do.
         */
        if (conversationId !== id) {
          return;
        }

        const remaining =
          conversations.filter(
            (conversation) =>
              conversation.id !== id,
          );

        /*
         * Switch to another existing
         * conversation.
         */
        if (remaining.length > 0) {
          await handleSelectConversation(
            remaining[0].id,
          );

          return;
        }

        /*
         * No conversations remain,
         * so create a fresh one.
         */
        await createConversation(
          promptKey,
        );

        setMessages([]);
        setInput("");
      } catch (error) {
        console.error(
          "Failed to delete conversation:",
          error,
        );
      }
    };

  // ----------------------------------------
  // Render
  // ----------------------------------------

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex">
      <ConversationSidebar
        conversations={conversations}
        conversationId={conversationId}
        open={sidebarOpen}
        disabled={isLoading}
        onNewChat={handleNewChat}
        onSelect={handleSelectConversation}
        onDelete={
          handleDeleteConversation
        }
      />

      <main className="min-w-0 flex-1 flex flex-col min-h-screen">
        <ChatHeader
          promptKey={promptKey}
          disabled={isLoading}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() =>
            setSidebarOpen(
              (value) => !value,
            )
          }
          onPromptChange={setPromptKey}
        />

        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          loadingConversation={
            loadingConversation
          }
          error={error}
          onRegenerate={() =>
            void regenerate()
          }
          onStop={stop}
          bottomRef={bottomRef}
          onQuestionSelect={setInput}
        />

        <ChatInput
          input={input}
          disabled={
            !conversationId ||
            isLoading
          }
          isLoading={isLoading}
          promptKey={promptKey}
          onInputChange={setInput}
          onSubmit={handleSubmit}
        />
      </main>
    </div>
  );
}
