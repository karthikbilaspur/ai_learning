USER INPUT
                            (e.g., "Analyze Notion")
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │       FASTAPI BACKEND         │
                       │   (Server-Sent Events / SSE)  │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │       LANGGRAPH ENGINE        │
                       └───────────────┬───────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
  ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
  │   SCOUT AGENT     │      │   ANALYST AGENT   │      │   CRITIC AGENT    │
  │                   │      │                   │      │                   │
  │ • Tavily Search   │ ───► │ • Extracts JSON   │ ───► │ • Audits Gaps     │
  │ • Firecrawl Web   │      │ • Pydantic Models │      │ • Reflects / Loops│
  │   Scraper         │      │ • Normalizes Data │      │ • Drafts Report   │
  └───────────────────┘      └───────────────────┘      └─────────┬─────────┘
                                                                  │
            ┌─────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────┐
│     OUTPUT STACK      │
├───────────────────────┤
│ 💾 SQLite Database    │ ───► Saved History
│ 📄 ReportLab PDF      │ ───► Downloadable Report
│ ⚡ React Frontend      │ ───► Live Stream Logs & Markdown UI
└───────────────────────┘