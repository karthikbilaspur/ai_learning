export type ToolKind = "info" | "data" | "action";

export interface Tool {
  path: string;
  name: string;
  description: string;
  example: string;
  kind: ToolKind;
}

export interface TraceEvent {
  type: "tool_call" | "tool_result";
  name: string;
  round: number;
  args?: Record<string, unknown>;
  result?: unknown;
}

export interface PendingCall {
  name: string;
  args: Record<string, unknown>;
}

export interface AgentResponse {
  answer?: string;
  trace: TraceEvent[];
  rounds: number;
  needsConfirmation?: boolean;
  sessionId?: string;
  pendingCall?: PendingCall;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
