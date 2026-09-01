import { streamText, type UIMessage } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { db } from "@/lib/db";
import { env } from "@/lib/env";
import { rateLimit } from "@/lib/rate-limit";
import { calculateCost } from "@/lib/tokens";
import { SYSTEM_PROMPTS, type PromptKey } from "@/lib/prompts";
import { estimateInputTokens, getMessageText } from "@/lib/chat";
import { getClientIp, jsonError } from "@/lib/http";
import { z } from "zod";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const openai = createOpenAI({ apiKey: env.OPENAI_API_KEY });

const requestSchema = z.object({
  messages: z.array(z.any()).min(1),
  conversationId: z.string().cuid(),
  systemPromptKey: z.enum(["default", "codingExpert", "writer", "teacher"]).default("default"),
});

export async function POST(request: Request) {
  const ip = getClientIp(request);
  const rl = await rateLimit(ip);

  if (!rl.success) {
    return jsonError("Too many requests. Please try again later.", 429, {
      retryAfter: Math.max(1, Math.ceil((rl.resetAt - Date.now()) / 1000)),
    });
  }

  try {
    const body = await request.json();
    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) return jsonError("Invalid chat request.", 400);

    const { messages, conversationId, systemPromptKey } = parsed.data as {
      messages: UIMessage[];
      conversationId: string;
      systemPromptKey: PromptKey;
    };

    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== "user") return jsonError("The latest message must be from the user.", 400);

    const lastText = getMessageText(lastMessage);
    if (!lastText.trim()) return jsonError("Message cannot be empty.", 400);
    if (lastText.length > env.MAX_MESSAGE_CHARS) {
      return jsonError(`Message is too long. Maximum is ${env.MAX_MESSAGE_CHARS.toLocaleString()} characters.`, 413);
    }

    const inputTokens = estimateInputTokens(messages);
    if (inputTokens > env.MAX_INPUT_TOKENS) {
      return jsonError(`Conversation context is too large (${inputTokens.toLocaleString()} tokens). Start a new chat or shorten the conversation.`, 413);
    }

    const conversation = await db.conversation.findUnique({ where: { id: conversationId } });
    if (!conversation) return jsonError("Conversation not found.", 404);

    // Persist the user message before streaming. Avoid duplicating it when the client
    // asks the server to regenerate an existing turn.
    const latestStored = await db.message.findFirst({
      where: { conversationId },
      orderBy: { createdAt: "desc" },
      select: { role: true, content: true },
    });

    if (!(latestStored?.role === "user" && latestStored.content === lastText)) {
      await db.message.create({
        data: { conversationId, role: "user", content: lastText },
      });
    }

    if (conversation.title === "New chat") {
      await db.conversation.update({ where: { id: conversationId }, data: { title: lastText.slice(0, 80) } });
    }

    const result = streamText({
      model: openai(env.OPENAI_MODEL),
      system: SYSTEM_PROMPTS[systemPromptKey],
      messages,
      temperature: 0.7,
      onFinish: async ({ usage, text }) => {
        const inTokens = Number(usage.inputTokens ?? inputTokens);
        const outTokens = Number(usage.outputTokens ?? 0);
        const cost = calculateCost(env.OPENAI_MODEL, inTokens, outTokens);

        try {
          await db.message.create({
            data: {
              conversationId,
              role: "assistant",
              content: text,
              inputTokens: inTokens,
              outputTokens: outTokens,
              estimatedCost: cost.total,
            },
          });
          await db.conversation.update({ where: { id: conversationId }, data: {} });
        } catch (error) {
          console.error("[CHAT_PERSIST_ASSISTANT]", error);
        }

        console.info("[CHAT_USAGE]", JSON.stringify({
          conversationId,
          model: env.OPENAI_MODEL,
          inputTokens: inTokens,
          outputTokens: outTokens,
          estimatedCostUsd: Number(cost.total.toFixed(8)),
        }));
      },
    });

    return result.toUIMessageStreamResponse({
      headers: {
        "X-RateLimit-Remaining": String(rl.remaining),
        "X-Input-Tokens": String(inputTokens),
      },
    });
  } catch (error) {
    console.error("[CHAT_API_ERROR]", error);
    return jsonError("Something went wrong while generating the response.", 500);
  }
}
