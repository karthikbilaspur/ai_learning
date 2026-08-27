# AI Agent Tool Calling Demo

A React + TypeScript frontend and Node.js backend demonstrating:

User → LLM → tool decision → JavaScript function/API → tool result → LLM → final response

## Included tools

1. `calculate` — restricted arithmetic
2. `search_dataset` — searches an employee dataset
3. `analyze_dataset` — calculates dataset statistics
4. `get_weather` — live Open-Meteo weather
5. `convert_currency` — live Frankfurter exchange rates
6. `get_time` — current time for an IANA timezone
7. `search_web` — DuckDuckGo Instant Answer API
8. `lookup_products` — local product catalog
9. `create_task` — an actual state-changing demo action

The UI has a separate tool page/selection for each tool. `App`/`main.tsx` is the single entry point that runs the demo.

## Requirements

- Node.js 18+ (20+ recommended)
- An OpenAI API key

## Run

1. Copy `.env.example` to `.env`
2. Put your API key in `.env`
3. Install dependencies:

```bash
npm install
```

4. Start backend:

```bash
npm run server
```

5. In another terminal start frontend:

```bash
npm run dev
```

Open the Vite URL shown in the terminal, normally http://localhost:5173.

Or run both:

```bash
npm run dev:all
```

## Important architecture note

The browser never receives the OpenAI API key. The React app calls `/api/agent`; the Node server calls the LLM and executes approved server-side tools.

## Agentic behavior

This demo is more than a one-shot tool call: the backend loops up to 8 turns. After each tool result, the LLM can decide whether another tool is needed. This enables multi-step tasks such as:

> Find engineering employees and calculate their average salary.

or:

> Find laptops under 80000 and compare the returned prices.

## Security note

The calculator uses a restricted character whitelist for this demo. For production, replace it with a dedicated math parser. Never expose arbitrary code execution or shell execution as an LLM tool.