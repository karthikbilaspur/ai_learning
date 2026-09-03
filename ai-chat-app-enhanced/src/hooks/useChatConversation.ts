"use client";

import {
  useMemo,
} from "react";

import {
  DefaultChatTransport,
} from "ai";

import {
  useChat,
} from "@ai-sdk/react";

import type { PromptKey } from "@/lib/prompts";

type UseChatConversationOptions = {
  conversationId: string | null;
  promptKey: PromptKey;
};

export function useChatConversation({
  conversationId,
  promptKey,
}: UseChatConversationOptions) {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",

        body: () => ({
          conversationId,
          systemPromptKey:
            promptKey,
        }),
      }),
    [
      conversationId,
      promptKey,
    ],
  );

  const chat = useChat({
    transport,
  });

  const isLoading =
    chat.status === "streaming" ||
    chat.status === "submitted";

  return {
    ...chat,
    isLoading,
  };
}