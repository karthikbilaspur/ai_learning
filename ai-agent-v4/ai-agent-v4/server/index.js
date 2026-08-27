import "dotenv/config";
import express from "express";
import cors from "cors";
import crypto from "node:crypto";
import OpenAI from "openai";
import { toolDefinitions, executeTool, requiresConfirmation } from "./tools.js";
import { createSession, getSession, deleteSession } from "./sessions.js";

const app = express();

// New in v4: CORS is locked to a configured origin instead of `cors()`
// (any origin), so a random site can't call your OpenAI-backed API from
// a visitor's browser.
const allowedOrigin = process.env.FRONTEND_ORIGIN || "http://localhost:5173";
app.use(cors({ origin: allowedOrigin }));
app.use(express.json());

// New in v4: a small in-memory rate limiter (20 requests/minute/IP). Not a
// substitute for a real limiter (e.g. behind a proxy that sets req.ip
// correctly, or Redis-backed for multi-instance deployments) but it stops
// a single client from silently burning your OpenAI quota.
const requestLog = new Map();
function rateLimit(req, res, next) {
  const ip = req.ip;
  const now = Date.now();
  const windowMs = 60_000;
  const max = 20;
  const timestamps = (requestLog.get(ip) || []).filter((t) => now - t < windowMs);
  if (timestamps.length >= max) {
    return res.status(429).json({ error: "Too many requests. Please slow down and try again shortly." });
  }
  timestamps.push(now);
  requestLog.set(ip, timestamps);
  next();
}

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";

const system = `You are a responsible AI agent. Complete user goals with tools.
You may call multiple tools sequentially; a previous result may determine the next action.
Never claim a tool action happened unless its result confirms it.
Do not expose private chain-of-thought; summarize actions and results only.`;

app.get("/api/health", (_, res) => res.json({ ok: true, model }));

/**
 * Runs the tool-calling loop starting at `messages`, from round `startRound`.
 * Returns either a finished answer, or - new in v4 - pauses and returns a
 * pending confirmation if the model wants to call a tool in
 * `requiresConfirmation` (see tools.js).
 *
 * Simplification: if a round contains several tool calls and one of them
 * needs confirmation, any calls after it in that same round are not yet
 * executed - they'll be picked up again after the round resumes via
 * /api/agent/confirm. This keeps the demo simple; a production version
 * would resolve all calls in a round together.
 */
async function runLoop(messages, trace, startRound) {
  for (let round = startRound; round <= 8; round++) {
    const r = await client.chat.completions.create({ model, messages, tools: toolDefinitions, tool_choice: "auto" });
    const m = r.choices[0].message;
    messages.push(m);

    if (!m.tool_calls?.length) {
      return { done: true, answer: m.content || "", trace, rounds: round };
    }

    for (const c of m.tool_calls) {
      if (requiresConfirmation.has(c.function.name)) {
        return {
          done: false,
          pendingCall: { name: c.function.name, args: JSON.parse(c.function.arguments || "{}") },
          trace,
          rounds: round,
          messages,
          round,
        };
      }

      const args = JSON.parse(c.function.arguments || "{}");
      trace.push({ type: "tool_call", name: c.function.name, args, round });
      let result;
      try {
        result = await executeTool(c.function.name, args);
      } catch (e) {
        result = { error: e.message || "tool failed" };
      }
      trace.push({ type: "tool_result", name: c.function.name, result, round });
      messages.push({ role: "tool", tool_call_id: c.id, content: JSON.stringify(result) });
    }
  }
  return { done: true, answer: "The agent reached its 8-step limit.", trace, rounds: 8 };
}

function respondWithOutcome(res, outcome) {
  if (!outcome.done) {
    const sessionId = crypto.randomUUID();
    createSession(sessionId, { messages: outcome.messages, round: outcome.round });
    return res.json({
      needsConfirmation: true,
      sessionId,
      pendingCall: outcome.pendingCall,
      trace: outcome.trace,
      rounds: outcome.rounds,
    });
  }
  res.json({ answer: outcome.answer, trace: outcome.trace, rounds: outcome.rounds });
}

app.post("/api/agent", rateLimit, async (req, res) => {
  try {
    const { message, history = [] } = req.body;
    if (!message) return res.status(400).json({ error: "message required" });

    const messages = [
      { role: "system", content: system },
      ...history.filter((x) => ["user", "assistant"].includes(x.role)).slice(-12),
      { role: "user", content: message },
    ];
    const trace = [];

    const outcome = await runLoop(messages, trace, 1);
    respondWithOutcome(res, outcome);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message || "server error" });
  }
});

// New in v4: resumes a paused session after the user approves or rejects
// a confirmation-gated tool call (see requiresConfirmation in tools.js).
app.post("/api/agent/confirm", rateLimit, async (req, res) => {
  try {
    const { sessionId, approve } = req.body;
    const session = sessionId && getSession(sessionId);
    if (!session) return res.status(404).json({ error: "This confirmation has expired. Please try your request again." });

    const { messages, round } = session;
    const lastAssistantMsg = [...messages].reverse().find((msg) => msg.role === "assistant" && msg.tool_calls?.length);
    const call = lastAssistantMsg?.tool_calls?.find((c) => requiresConfirmation.has(c.function.name));

    if (!call) {
      deleteSession(sessionId);
      return res.status(400).json({ error: "No pending confirmation found for this session." });
    }

    const args = JSON.parse(call.function.arguments || "{}");
    const trace = [{ type: "tool_call", name: call.function.name, args, round }];
    const result = approve
      ? await executeTool(call.function.name, args).catch((e) => ({ error: e.message || "tool failed" }))
      : { rejected: true, reason: "User declined to run this action." };
    trace.push({ type: "tool_result", name: call.function.name, result, round });
    messages.push({ role: "tool", tool_call_id: call.id, content: JSON.stringify(result) });

    deleteSession(sessionId);
    const outcome = await runLoop(messages, trace, round + 1);
    respondWithOutcome(res, outcome);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message || "server error" });
  }
});

const port = Number(process.env.PORT || 3001);
app.listen(port, () => console.log(`Agent API on http://localhost:${port}`));
