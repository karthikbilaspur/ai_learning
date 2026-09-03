"use client";

import {
  useCallback,
  useState,
} from "react";

import type { PromptKey } from "@/lib/prompts";
import type {
  Conversation,
  StoredMessage,
} from "@/types/chat";

type ConversationResponse = {
  conversation: Conversation;
};

type ConversationsResponse = {
  conversations: Conversation[];
};

type ConversationDetailResponse = {
  conversation: Conversation & {
    messages: StoredMessage[];
  };
};

export function useConversations() {
  const [
    conversations,
    setConversations,
  ] = useState<Conversation[]>([]);

  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const loadConversations =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/conversations",
          {
            cache: "no-store",
          },
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load conversations",
          );
        }

        const data =
          (await response.json()) as ConversationsResponse;

        setConversations(
          data.conversations,
        );

        return data.conversations;
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Unable to load conversations";

        setError(message);
        throw error;
      } finally {
        setLoading(false);
      }
    }, []);

  const createConversation =
    useCallback(
      async (
        promptKey: PromptKey = "default",
      ) => {
        setError(null);

        const response = await fetch(
          "/api/conversations",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              promptKey,
            }),
          },
        );

        if (!response.ok) {
          throw new Error(
            "Unable to create conversation",
          );
        }

        const data =
          (await response.json()) as ConversationResponse;

        const conversation =
          data.conversation;

        setConversations(
          (current) => [
            conversation,
            ...current.filter(
              (item) =>
                item.id !==
                conversation.id,
            ),
          ],
        );

        setConversationId(
          conversation.id,
        );

        return conversation;
      },
      [],
    );

  const getConversation =
    useCallback(
      async (id: string) => {
        const response = await fetch(
          `/api/conversations/${id}`,
          {
            cache: "no-store",
          },
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load conversation",
          );
        }

        const data =
          (await response.json()) as ConversationDetailResponse;

        return data.conversation;
      },
      [],
    );

  const selectConversation =
    useCallback(
      async (id: string) => {
        setLoading(true);
        setError(null);

        try {
          const conversation =
            await getConversation(id);

          setConversationId(id);

          return conversation;
        } catch (error) {
          const message =
            error instanceof Error
              ? error.message
              : "Unable to load conversation";

          setError(message);
          throw error;
        } finally {
          setLoading(false);
        }
      },
      [getConversation],
    );

  const deleteConversation =
    useCallback(
      async (id: string) => {
        setError(null);

        const response = await fetch(
          `/api/conversations/${id}`,
          {
            method: "DELETE",
          },
        );

        if (!response.ok) {
          throw new Error(
            "Unable to delete conversation",
          );
        }

        setConversations(
          (current) =>
            current.filter(
              (conversation) =>
                conversation.id !== id,
            ),
        );

        setConversationId(
          (current) =>
            current === id
              ? null
              : current,
        );
      },
      [],
    );

  return {
    conversations,
    conversationId,

    loading,
    error,

    loadConversations,
    createConversation,
    getConversation,
    selectConversation,
    deleteConversation,

    setConversationId,
  };
}