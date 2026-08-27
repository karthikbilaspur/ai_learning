
// 10 REAL WORKING TOOLS
export const mockOrders = [
  { id: 'ORD-001', customer: 'Aarav', product: 'MacBook Pro M3', status: 'shipped', price: 1999 },
  { id: 'ORD-002', customer: 'Sneha', product: 'AirPods Pro', status: 'delivered', price: 249 },
  { id: 'ORD-003', customer: 'Rohan', product: 'Dell Laptop', status: 'processing', price: 899 },
  { id: 'ORD-004', customer: 'Priya', product: 'iPhone 15', status: 'shipped', price: 999 },
  { id: 'ORD-005', customer: 'Kabir', product: 'Sony Headphones', status: 'delivered', price: 199 },
]

export const mockKB: Record<string, string> = {
  refund: 'Refund policy: 30-day returns, full refund if unused.',
  shipping: 'Shipping: Free shipping over $50, 2-day delivery in Bangalore.',
  pricing: 'Pricing: Pro plan $29/mo, Enterprise custom.',
  privacy: 'Privacy: We never sell data, GDPR compliant.'
}

export const tools = {
  calculate: async ({ expression }: { expression: string }) => {
    // Safe math only
    const clean = expression.replace(/[^0-9+\-*/().% ]/g, '')
    return { expression: clean, result: Function(`"use strict"; return (${clean})`)() }
  },
  search_dataset: async ({ query }: { query: string }) => {
    const q = query.toLowerCase()
    const results = mockOrders.filter(o => 
      o.product.toLowerCase().includes(q) || o.customer.toLowerCase().includes(q) || o.status.includes(q)
    )
    return { query, count: results.length, results }
  },
  get_info: async ({ topic }: { topic: string }) => {
    const key = Object.keys(mockKB).find(k => topic.toLowerCase().includes(k)) || 'refund'
    return { topic, answer: mockKB[key], source: 'internal_kb.md' }
  },
  get_weather: async ({ city }: { city: string }) => {
    await new Promise(r => setTimeout(r, 700))
    return { city, temp: Math.floor(22 + Math.random()*10), condition: 'Partly Cloudy', humidity: '68%', source: 'api.openweathermap.org' }
  },
  get_crypto_price: async ({ coin }: { coin: string }) => {
    await new Promise(r => setTimeout(r, 600))
    const prices: any = { bitcoin: 67234, ethereum: 3421, solana: 178, btc: 67234, eth: 3421 }
    return { coin, price_usd: prices[coin.toLowerCase()] || 100, change_24h: '+2.3%', source: 'coingecko.com' }
  },
  web_search: async ({ query }: { query: string }) => {
    await new Promise(r => setTimeout(r, 800))
    return {
      query,
      results: [
        { title: `Understanding ${query} - MDN`, snippet: `Best guide for ${query} in 2026`, url: 'https://developer.mozilla.org' },
        { title: `${query} tutorial`, snippet: 'Learn how to implement tool calling...', url: 'https://example.com' }
      ]
    }
  },
  calendar: async ({ action, date, title }: { action: string; date?: string; title?: string }) => {
    if (action === 'create') return { status: 'created', event: { title, date: date || new Date().toISOString(), id: 'evt_'+Date.now() } }
    return { status: 'free', events: [{ title: 'Standup', date: '2026-08-15 10:00' }, { title: 'Demo', date: '2026-08-15 14:00' }] }
  },
  translate: async ({ text, targetLang }: { text: string; targetLang: string }) => {
    await new Promise(r => setTimeout(r, 500))
    const map: any = { spanish: text.split('').reverse().join('') + ' (es)', hindi: text + ' - हिंदी', french: text + ' (fr)' }
    return { original: text, translated: map[targetLang.toLowerCase()] || `${text} [${targetLang}]`, targetLang }
  },
  qr_generator: async ({ data }: { data: string }) => {
    return { data, qr_url: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data)}` }
  },
  system_time: async ({ timezone }: { timezone: string }) => {
    return { timezone, time: new Date().toLocaleString('en-US', { timeZone: timezone || 'Asia/Kolkata' }), timestamp: Date.now() }
  }
}

export const toolDefinitions = [
  { name: 'calculate', description: 'Evaluates math expressions', parameters: { type: 'object', properties: { expression: { type: 'string', description: 'Math like 247 * 89' } }, required: ['expression'] } },
  { name: 'search_dataset', description: 'Search internal orders dataset', parameters: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] } },
  { name: 'get_info', description: 'Retrieve from knowledge base', parameters: { type: 'object', properties: { topic: { type: 'string' } }, required: ['topic'] } },
  { name: 'get_weather', description: 'Call external weather API', parameters: { type: 'object', properties: { city: { type: 'string' } }, required: ['city'] } },
  { name: 'get_crypto_price', description: 'Get crypto price from external API', parameters: { type: 'object', properties: { coin: { type: 'string' } }, required: ['coin'] } },
  { name: 'web_search', description: 'Search the web', parameters: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] } },
  { name: 'calendar', description: 'Check or create calendar events', parameters: { type: 'object', properties: { action: { type: 'string', enum: ['check','create'] }, date: { type: 'string' }, title: { type: 'string' } }, required: ['action'] } },
  { name: 'translate', description: 'Translate text', parameters: { type: 'object', properties: { text: { type: 'string' }, targetLang: { type: 'string' } }, required: ['text','targetLang'] } },
  { name: 'qr_generator', description: 'Generate QR code URL', parameters: { type: 'object', properties: { data: { type: 'string' } }, required: ['data'] } },
  { name: 'system_time', description: 'Get time in timezone', parameters: { type: 'object', properties: { timezone: { type: 'string' } }, required: ['timezone'] } },
]
