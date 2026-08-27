import "dotenv/config";
import express from "express";
import cors from "cors";
import OpenAI from "openai";
import { tools, executeTool } from "./tools.js";

const app = express();
app.use(cors());
app.use(express.json());

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";

app.get("/api/health", (_, res) => res.json({ ok: true }));

app.post("/api/agent", async (req, res) => {
  try {
    const { message } = req.body;
    if (!message || typeof message !== "string") {
      return res.status(400).json({ error: "message is required" });
    }

    const messages = [
      {
        role: "system",
        content:
          "You are a helpful tool-using AI agent. Use tools when they improve accuracy. " +
          "You may call multiple tools sequentially. After each tool result, decide whether " +
          "another tool is needed to complete the user's goal. Never claim a tool was used unless it was."
      },
      { role: "user", content: message }
    ];

    const trace = [];

    for (let turn = 0; turn < 8; turn++) {
      const response = await client.chat.completions.create({
        model,
        messages,
        tools,
        tool_choice: "auto"
      });

      const assistant = response.choices[0].message;
      messages.push(assistant);

      if (!assistant.tool_calls?.length) {
        return res.json({
          answer: assistant.content || "I could not produce an answer.",
          trace
        });
      }

      for (const call of assistant.tool_calls) {
        const args = JSON.parse(call.function.arguments || "{}");
        trace.push({ type: "tool_call", name: call.function.name, args });

        let result;
        try {
          result = await executeTool(call.function.name, args);
        } catch (err) {
          result = { error: err instanceof Error ? err.message : "Tool failed" };
        }

        trace.push({ type: "tool_result", name: call.function.name, result });

        messages.push({
          role: "tool",
          tool_call_id: call.id,
          content: JSON.stringify(result)
        });
      }
    }

    res.json({
      answer: "The agent reached its maximum tool steps. Try a smaller task.",
      trace
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({
      error: err instanceof Error ? err.message : "Server error"
    });
  }
});

app.listen(process.env.PORT || 3001, () => {
  console.log(`Agent API running on http://localhost:${process.env.PORT || 3001}`);
});