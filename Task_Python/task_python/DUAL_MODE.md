
# Dual Mode - Standalone + Together

This project supports BOTH modes.

### 1. STANDALONE MODE (your original files)

Each original script still works exactly as before:

```bash
# Original location
python original_scripts/Reddit_Analysis.py
python original_scripts/Rescale_Image.py
python original_scripts/Rename_Files.py
python original_scripts/Restuarant_Management.py  # launches Tkinter
python original_scripts/Tower_Defense.py  # launches Pygame window
python original_scripts/Reverse_Tower.py
```

Plus new standalone wrappers that use production logic without needing Docker:

```bash
# Without API, direct tool call
python standalone/run_reddit_analysis.py '{"subreddit":"python","num_posts":5,"analysis_type":"title"}'
python standalone/run_tower_defense.py '{"towers":[{"x":100,"y":100}],"num_enemies":10}'
python standalone/run_file_tools.py '{"directory":"/app/data","old_name":"test","new_name":"prod"}'
```

### 2. TOGETHER MODE (Agent + Docker + Auth + Monitoring)

All 9 tools registered in one orchestrator:

```bash
docker-compose up --build
# All tools available via:
POST /api/agent/run {"tool": "reddit_analysis", "params": {...}}
POST /api/agent/run {"tool": "rename_files", "params": {...}}
POST /api/agent/run {"tool": "tower_defense", "params": {...}}
```

Flow:
original_scripts/*.py  --(refactored)--> src/agent/tools/*.py --(registered)--> src/agent/core.py TOOL_REGISTRY --(exposed)--> FastAPI /api/agent/run

You can:
- Run one tool alone (standalone)
- Run all tools via one API (together)
- Mix: call AgentOrchestrator from any Python script without FastAPI:

```python
from src.agent.core import AgentOrchestrator
agent = AgentOrchestrator()
print(agent.execute("rescale_image", {"image_path": "/app/data/img.jpg", "width": 512, "height": 512}))
print(agent.execute("reddit_analysis", {"subreddit": "memes", "num_posts": 10}))
```

### Architecture for dual mode:

original_scripts/  (legacy CLI / GUI)
      |
      v (logic preserved)
src/agent/tools/  (production wrappers with logging + allowlist + error handling)
      |
      v
src/agent/core.py  (TOOL_REGISTRY - runs any tool)
      |
      +--> standalone/run_*.py (direct)
      +--> FastAPI (with Auth, DB logging, Prometheus)

So yes: standalone = works, together = works, and you can import orchestrator anywhere.
