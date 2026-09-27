import {
  isPromptKey,
  type PromptKey,
} from "@/lib/prompts";

export const MAX_MESSAGE_LENGTH = 30_000;

export const MAX_CONVERSATION_TITLE_LENGTH =
  120;

export type ChatRequestInput = {
  conversationId: string;
  systemPromptKey: PromptKey;
};

export function isNonEmptyString(
  value: unknown,
): value is string {
  return (
    typeof value === "string" &&
    value.trim().length > 0
  );
}

export function validateConversationId(
  value: unknown,
): string {
  if (!isNonEmptyString(value)) {
    throw new Error(
      "conversationId is required",
    );
  }

  return value.trim();
}

export function validatePromptKey(
  value: unknown,
): PromptKey {
  if (!isPromptKey(value)) {
    throw new Error(
      "Invalid system prompt",
    );
  }

  return value;
}

export function validateMessage(
  value: unknown,
): string {
  if (!isNonEmptyString(value)) {
    throw new Error(
      "Message cannot be empty",
    );
  }

  const message = value.trim();

  if (
    message.length >
    MAX_MESSAGE_LENGTH
  ) {
    throw new Error(
      `Message cannot exceed ${MAX_MESSAGE_LENGTH.toLocaleString()} characters`,
    );
  }

  return message;
}