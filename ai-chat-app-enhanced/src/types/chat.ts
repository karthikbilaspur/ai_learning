import type { PromptKey } from "@/lib/prompts";

export type Conversation = {
  id: string;
  title: string;
  promptKey: PromptKey;
  createdAt: string;
  updatedAt: string;
};

export type StoredMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
};