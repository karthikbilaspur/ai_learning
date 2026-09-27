import type { AgentResponse, ChatMessage } from "../types";

const BASE_URL = "http://localhost:3001";

async function post(path: string, body: unknown): Promise<AgentResponse> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

export function runAgent(message: string, history: ChatMessage[]): Promise<AgentResponse> {
  return post("/api/agent", { message, history });
}

export function confirmAgent(sessionId: string, approve: boolean): Promise<AgentResponse> {
  return post("/api/agent/confirm", { sessionId, approve });
}
