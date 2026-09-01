import type { UIMessage } from "ai";
import { countTokens } from "@/lib/tokens";

export function uiMessagesToText(messages: UIMessage[]) {
  return messages
    .map((message) => {
      const text = message.parts
        .filter((part) => part.type === "text")
        .map((part) => part.text)
        .join("");
      return `${message.role}: ${text}`;
    })
    .join("\n");
}

export function getMessageText(message: UIMessage) {
  return message.parts
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("");
}

export function estimateInputTokens(messages: UIMessage[]) {
  return countTokens(uiMessagesToText(messages));
}
