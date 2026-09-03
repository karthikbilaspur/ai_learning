
# task_python - Productionized Unified Tool Agent

Converted 9 standalone Python scripts into a single production-grade FastAPI agent.

### Original Scripts → Tools
| File | New Tool | Endpoint |
|------|----------|----------|
| Reddit_Analysis.py | `reddit_analysis` | POST /api/agent/run |
| Reddit_Flair.py | `reddit_flair` | |
| Reddit_Meme_Scrapper.py | `meme_scrapper` | |
| Rename_Files.py | `rename_files` | |
| Rename_Files_Wtih_Time.py | `rename_with_time` | |
| Rescale_Image.py | `rescale_image` | |
| Restuarant_Management.py | `restaurant` | |
| Reverse_Tower.py | `reverse_tower` | |
| Tower_Defense.py | `tower_defense` | |

### Tech Stack
- **API:** FastAPI + Uvicorn + Pydantic v2
- **DB:** PostgreSQL + SQLAlchemy 2.0 + Alembic (migrations)
- **Auth:** JWT (OAuth2PasswordBearer) + bcrypt + RBAC
- **Logging:** structlog JSON logging to stdout + logs/
- **Error Handling:** Centralized AppException handlers + allowlist checks
- **Monitoring:** /health, /metrics (Prometheus), Prometheus + Grafana via docker-compose
- **Config:** pydantic-settings + .env validation at startup
- **Docker:** Multi-stage Dockerfile + docker-compose with Postgres + Prometheus

### Architecture Diagram

```mermaid
graph TB
    Client -->|JWT| FastAPI[FastAPI src/main.py]
    FastAPI --> Auth[src/auth.py - RBAC]
    FastAPI --> Router[src/api/routes.py]
    Router --> Agent[src/agent/core.py - TOOL_REGISTRY]
    Agent --> Tools
    subgraph Tools [9 Tools]
      T1[reddit_analysis]
      T2[reddit_flair]
      T3[meme_scrapper]
      T4[file_tools - rename, rescale]
      T5[restaurant_mgmt]
      T6[tower_defense + reverse]
    end
    Tools --> DB[(Postgres - users, task_logs)]
    Tools --> Logger[structlog JSON]
    FastAPI --> Metrics[/metrics Prometheus]
    Metrics --> Prometheus[Prometheus:9090]
    Prometheus --> Grafana

    subgraph Docker
      FastAPI
      DB
      Prometheus
    end
```

### How to Run

```bash
cp .env.example .env
# edit JWT_SECRET

# With Docker (recommended)
docker-compose up --build
# API -> http://localhost:8000/docs
# Metrics -> http://localhost:8000/metrics
# Prometheus -> http://localhost:9090

# Migrations
docker-compose exec api alembic revision --autogenerate -m "init"
docker-compose exec api alembic upgrade head

# Local dev without docker
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Auth Flow
1. POST /api/auth/register {"username","email","password"}
2. POST /api/auth/login -> returns JWT
3. Use Authorization: Bearer <token> for /api/agent/run

### Monitoring & Logging
- All tool calls logged as JSON: {user_id, tool, duration_ms, status}
- Failed calls go to task_logs table
- /health checks DB connection
- /metrics exposes http_requests_total and latency

### Security Improvements over original scripts
- Path allowlist: file operations restricted to /app/data
- Input validation via Pydantic (no ../ traversal)
- No hardcoded secrets - via pydantic-settings
- Error handling prevents stack trace leak
- Auth required for all tool execution
