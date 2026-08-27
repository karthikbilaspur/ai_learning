# AI Tool-Calling Assistant - React/TS

Real Vite + React + TypeScript app with 10 tools.

## Install & Run
npm install
npm run dev
# open http://localhost:3000

## Flow Implemented
User → LLM (detectTool) → tool decision JSON → JavaScript function/API → result → LLM → response

## 10 Tools
1. calculate - math
2. search_dataset - your DB
3. get_info - knowledge base / RAG
4. get_weather - external API mock
5. get_crypto_price - external API mock
6. web_search - web search
7. calendar - check/create events
8. translate - translation API mock
9. qr_generator - generates QR URL
10. system_time - timezone

Replace detectTool() with real OpenAI function calling:
const res = await openai.chat.completions.create({ model: 'gpt-4o', tools: toolDefinitions, messages })
