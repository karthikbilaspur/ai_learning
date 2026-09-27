# AI Agent - 9 Tools

## Structure
backend/src/index.ts = server
backend/src/tools/index.ts = registry of 9 tools
backend/src/agents/orchestrator.ts = agent brain

## Run
cd backend
npm install
cp .env.example .env (add OPENAI_API_KEY)
npm run dev

## Test
curl -X POST http://localhost:4000/api/chat -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"calc 25*48"}]}'
