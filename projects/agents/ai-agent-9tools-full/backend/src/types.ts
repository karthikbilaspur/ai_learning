export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ToolCall {
  toolName: string;
  args: any;
  result?: any;
}
