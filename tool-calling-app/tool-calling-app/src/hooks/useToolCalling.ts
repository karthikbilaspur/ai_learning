
import { useState } from 'react'
import { tools } from '../tools'
import { ChatMessage, ToolCall } from '../types'

function detectTool(input: string): ToolCall | null {
  const lower = input.toLowerCase()
  if (/[0-9]+\s*[+*/%-]\s*[0-9]/.test(input) || lower.includes('calculate')) {
    const expr = input.match(/[0-9+\-*/().% ]+/)?.[0] || '2+2'
    return { id: 'call_'+Date.now(), name: 'calculate', arguments: { expression: expr } }
  }
  if (lower.includes('order') || lower.includes('search') && lower.includes('laptop') || lower.includes('macbook')) return { id: 'call_'+Date.now(), name: 'search_dataset', arguments: { query: input } }
  if (lower.includes('refund') || lower.includes('shipping') || lower.includes('policy') || lower.includes('pricing')) return { id: 'call_'+Date.now(), name: 'get_info', arguments: { topic: input } }
  if (lower.includes('weather')) {
    const city = input.split('in')[1]?.trim() || 'Bangalore'
    return { id: 'call_'+Date.now(), name: 'get_weather', arguments: { city } }
  }
  if (lower.includes('bitcoin') || lower.includes('crypto') || lower.includes('price of')) return { id: 'call_'+Date.now(), name: 'get_crypto_price', arguments: { coin: lower.includes('eth') ? 'ethereum' : 'bitcoin' } }
  if (lower.includes('search web') || lower.includes('google') || lower.includes('react')) return { id: 'call_'+Date.now(), name: 'web_search', arguments: { query: input } }
  if (lower.includes('calendar') || lower.includes('meeting') || lower.includes('event')) return { id: 'call_'+Date.now(), name: 'calendar', arguments: { action: lower.includes('create') ? 'create' : 'check', title: input, date: new Date().toISOString() } }
  if (lower.includes('translate')) return { id: 'call_'+Date.now(), name: 'translate', arguments: { text: 'hello world', targetLang: 'spanish' } }
  if (lower.includes('qr')) return { id: 'call_'+Date.now(), name: 'qr_generator', arguments: { data: input } }
  if (lower.includes('time') && lower.includes('tokyo') || lower.includes('timezone')) return { id: 'call_'+Date.now(), name: 'system_time', arguments: { timezone: 'Asia/Tokyo' } }
  return null
}

export function useToolCalling() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isThinking, setIsThinking] = useState(false)
  const [logs, setLogs] = useState<any[]>([])

  async function send(input: string) {
    const userMsg: ChatMessage = { id: Date.now()+ '', role: 'user', content: input }
    setMessages(m => [...m, userMsg])
    setIsThinking(true)

    const toolCall = detectTool(input)
    let finalContent = ''

    if (toolCall) {
      const start = Date.now()
      // @ts-ignore
      const result = await (tools as any)[toolCall.name](toolCall.arguments)
      const latency = Date.now() - start
      setLogs(l => [...l, { id: toolCall.id, tool: toolCall.name, args: toolCall.arguments, result, latency }])

      // LLM grounding step
      if (toolCall.name === 'calculate') finalContent = `The result of ${result.expression} is **${result.result}**`
      else if (toolCall.name === 'search_dataset') finalContent = `Found ${result.count} orders: ${result.results.map((r:any)=>r.product).join(', ')}`
      else if (toolCall.name === 'get_weather') finalContent = `Weather in ${result.city}: ${result.temp}°C, ${result.condition}, Humidity ${result.humidity}`
      else if (toolCall.name === 'get_crypto_price') finalContent = `${result.coin} is $${result.price_usd} (${result.change_24h} 24h)`
      else if (toolCall.name === 'get_info') finalContent = result.answer
      else finalContent = `Tool ${toolCall.name} executed: \n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\``

      const assistantMsg: ChatMessage = { id: Date.now()+'a', role: 'assistant', content: finalContent, toolCalls: [toolCall], toolResults: [result] }
      setMessages(m => [...m, assistantMsg])
    } else {
      setMessages(m => [...m, { id: Date.now()+'a', role: 'assistant', content: `I can help! Try one of the tool examples. I have 10 tools: calculate, search_dataset, knowledge_base, weather, crypto, web_search, calendar, translate, qr_generator, system_time.` }])
    }
    setIsThinking(false)
  }

  return { messages, send, isThinking, logs }
}
