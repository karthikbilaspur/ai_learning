export interface ToolDefinition {
  name: string
  description: string
  parameters: { type: string; properties: Record<string, any>; required: string[] }
}

export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
}

export interface ExecutionLog {
  id: string
  tool: string
  args: any
  result: any
  latency: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'tool'
  content: string
  toolCalls?: ToolCall[]
  toolResults?: any[]
}
