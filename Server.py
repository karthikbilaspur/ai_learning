
"""
Production MCP Server v3 - Real World
Features: Postgres + JSON fallback, API Key Auth, Pydantic validation, Pagination, Analytics

Model -> MCP Client -> MCP Server (this file) -> Postgres (or JSON fallback) -> External System

Env:
  DATABASE_URL=postgresql://user:pass@localhost:5432/projects  # optional, falls back to JSON
  MCP_API_KEY=sk-secret-key  # optional, if set, all tools require x-api-key
  USE_JSON_FALLBACK=true  # set to true to force JSON even if DATABASE_URL exists
"""

import os
import json
import pathlib
import datetime
from typing import Optional, List, Literal
from contextlib import contextmanager

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

load_dotenv()

DB_PATH = pathlib.Path(__file__).parent / "project_db.json"
LOG_PATH = pathlib.Path(__file__).parent / "activity.log"

# --- Auth ---
API_KEY = os.getenv("MCP_API_KEY")

def check_auth(provided_key: Optional[str] = None):
    """If MCP_API_KEY is set, require it. In MCP, client passes via header or tool arg."""
    if not API_KEY:
        return True  # auth disabled for educational mode
    # Allow key via env or via tool arg
    key = provided_key or os.getenv("CLIENT_API_KEY") or os.getenv("X_API_KEY")
    # For Claude Desktop, you set env in config: {"env": {"CLIENT_API_KEY": "sk-..."}}
    if key != API_KEY:
        raise PermissionError(f"Unauthorized: Invalid API key. Expected key set in MCP_API_KEY.")
    return True

# --- DB Abstraction ---
class DB:
    def __init__(self):
        self.use_postgres = False
        self.conn_str = os.getenv("DATABASE_URL")
        if self.conn_str and os.getenv("USE_JSON_FALLBACK", "false").lower() != "true":
            try:
                import psycopg2
                self.psycopg2 = psycopg2
                # Test connection
                conn = psycopg2.connect(self.conn_str)
                conn.close()
                self.use_postgres = True
                print(f"[DB] Using Postgres: {self.conn_str[:30]}...")
                self._ensure_table()
            except Exception as e:
                print(f"[DB] Postgres failed ({e}), falling back to JSON")
                self.use_postgres = False
        if not self.use_postgres:
            print("[DB] Using JSON fallback:", DB_PATH)

    def _ensure_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('planning','active','in_progress','done','archived')),
            owner TEXT NOT NULL,
            stack JSONB DEFAULT '[]',
            deadline DATE,
            budget_usd INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        with self.pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                # Seed if empty
                cur.execute("SELECT COUNT(*) FROM projects")
                if cur.fetchone()[0] == 0 and DB_PATH.exists():
                    data = json.loads(DB_PATH.read_text())
                    for p in data.get("projects", []):
                        cur.execute(
                            "INSERT INTO projects (id,name,status,owner,stack,deadline,budget_usd) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                            (p["id"], p["name"], p["status"], p["owner"], json.dumps(p.get("stack",[])), p.get("deadline") or None, p.get("budget_usd",0))
                        )
                conn.commit()

    @contextmanager
    def pg_conn(self):
        conn = self.psycopg2.connect(self.conn_str)
        try:
            yield conn
        finally:
            conn.close()

    # JSON impl
    def _load_json(self):
        if not DB_PATH.exists():
            return {"projects": []}
        return json.loads(DB_PATH.read_text())

    def _save_json(self, data):
        DB_PATH.write_text(json.dumps(data, indent=2))
        with open(LOG_PATH, "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} save {len(data['projects'])}\n")

    # Unified API
    def list(self, status: Optional[str]=None, owner: Optional[str]=None, limit: int=50, offset: int=0):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    q = "SELECT id,name,status,owner,stack,deadline,budget_usd,created_at FROM projects WHERE 1=1"
                    params = []
                    if status:
                        q += " AND status=%s"; params.append(status)
                    if owner:
                        q += " AND owner ILIKE %s"; params.append(f"%{owner}%")
                    q += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                    cur.execute(q, params)
                    cols = [d[0] for d in cur.description]
                    return [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            data = self._load_json()["projects"]
            if status: data = [p for p in data if p["status"]==status]
            if owner: data = [p for p in data if owner.lower() in p["owner"].lower()]
            return data[offset:offset+limit]

    def get(self, project_id: str):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id,name,status,owner,stack,deadline,budget_usd FROM projects WHERE id=%s", (project_id,))
                    row = cur.fetchone()
                    if not row:
                        return None
                    cols = [d[0] for d in cur.description]
                    return dict(zip(cols, row))
        else:
            for p in self._load_json()["projects"]:
                if p["id"]==project_id:
                    return p
            return None

    def search(self, query: str, limit: int=20):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id,name,status,owner,stack FROM projects WHERE name ILIKE %s OR owner ILIKE %s OR stack::text ILIKE %s LIMIT %s",
                        (f"%{query}%", f"%{query}%", f"%{query}%", limit)
                    )
                    cols = [d[0] for d in cur.description]
                    return [dict(zip(cols, r)) for r in cur.fetchall()]
        else:
            q = query.lower()
            return [p for p in self._load_json()["projects"] if q in json.dumps(p).lower()][:limit]

    def create(self, proj: dict):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM projects")
                    count = cur.fetchone()[0]
                    pid = proj.get("id") or f"p{count+1}"
                    cur.execute(
                        "INSERT INTO projects (id,name,status,owner,stack,deadline,budget_usd) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                        (pid, proj["name"], proj["status"], proj["owner"], json.dumps(proj.get("stack",[])), proj.get("deadline"), proj.get("budget_usd",0))
                    )
                    conn.commit()
                    return self.get(pid)
        else:
            data = self._load_json()
            pid = f"p{len(data['projects'])+1}"
            proj["id"] = pid
            data["projects"].append(proj)
            self._save_json(data)
            return proj

    def update_status(self, project_id: str, new_status: str):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE projects SET status=%s, updated_at=NOW() WHERE id=%s RETURNING id", (new_status, project_id))
                    conn.commit()
                    if cur.rowcount==0:
                        return None
                    return self.get(project_id)
        else:
            data = self._load_json()
            for p in data["projects"]:
                if p["id"]==project_id:
                    p["status"]=new_status
                    self._save_json(data)
                    return p
            return None

    def analytics(self):
        if self.use_postgres:
            with self.pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT status, COUNT(*), SUM(budget_usd), AVG(budget_usd) FROM projects GROUP BY status")
                    by_status = [{"status": r[0], "count": r[1], "total_budget": r[2], "avg_budget": float(r[3] or 0)} for r in cur.fetchall()]
                    cur.execute("SELECT SUM(budget_usd), COUNT(*), MAX(budget_usd) FROM projects")
                    total, count, max_b = cur.fetchone()
                    cur.execute("SELECT owner, COUNT(*), SUM(budget_usd) FROM projects GROUP BY owner")
                    by_owner = [{"owner": r[0], "count": r[1], "budget": r[2]} for r in cur.fetchall()]
                    cur.execute("SELECT * FROM projects WHERE deadline < CURRENT_DATE AND status != 'done' AND status != 'archived'")
                    overdue = cur.rowcount
                    return {"by_status": by_status, "total_budget": total or 0, "total_projects": count, "max_budget": max_b, "by_owner": by_owner}
        else:
            projs = self._load_json()["projects"]
            by_status = {}
            by_owner = {}
            total = 0
            for p in projs:
                by_status[p["status"]] = by_status.get(p["status"], 0) + 1
                by_owner[p["owner"]] = by_owner.get(p["owner"], 0) + p.get("budget_usd",0)
                total += p.get("budget_usd",0)
            return {
                "total_projects": len(projs),
                "total_budget": total,
                "by_status": by_status,
                "by_owner": by_owner,
                "overdue_count": len([p for p in projs if p.get("deadline") and p["deadline"] < datetime.date.today().isoformat() and p["status"] not in ("done","archived")])
            }

db = DB()
mcp = FastMCP("project-db-prod")

# ============ Pydantic Schemas ============
class CreateProjectInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Project name")
    owner: str = Field(..., min_length=2, description="Owner name")
    status: Literal["planning","active","in_progress","done","archived"] = "planning"
    stack: str = Field("", description="Comma separated tech stack, e.g. Python,FastAPI")
    budget_usd: int = Field(0, ge=0, le=1_000_000)
    deadline: Optional[str] = Field(None, description="YYYY-MM-DD")
    api_key: Optional[str] = Field(None, description="API key if MCP_API_KEY is set on server")

class ListInput(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    api_key: Optional[str] = None

# ============ Resources ============
@mcp.resource("projects://all")
def res_all() -> str:
    return json.dumps(db.list(limit=100), indent=2, default=str)

@mcp.resource("projects://stats")
def res_stats() -> str:
    return json.dumps(db.analytics(), indent=2, default=str)

@mcp.resource("projects://activity")
def res_activity() -> str:
    if not LOG_PATH.exists():
        return "No activity yet"
    return LOG_PATH.read_text()[-3000:]

@mcp.resource("projects://{project_id}")
def res_one(project_id: str) -> str:
    proj = db.get(project_id)
    return json.dumps(proj or {"error":"not found"}, indent=2, default=str)

# ============ Tools ============
@mcp.tool()
def list_projects(status: str = "", owner: str = "", limit: int = 20, offset: int = 0, api_key: str = "") -> str:
    """List projects with filtering + pagination. Use status filter e.g. active, limit 1-100."""
    check_auth(api_key)
    result = db.list(status=status or None, owner=owner or None, limit=limit, offset=offset)
    return json.dumps(result, indent=2, default=str)

@mcp.tool()
def get_project(project_id: str, api_key: str = "") -> str:
    """Get one project by ID."""
    check_auth(api_key)
    proj = db.get(project_id)
    if not proj:
        return json.dumps({"error": "not found", "hint": "Use list_projects to see IDs"})
    return json.dumps(proj, indent=2, default=str)

@mcp.tool()
def search_projects(query: str, limit: int = 20, api_key: str = "") -> str:
    """Search by name, owner, or stack."""
    check_auth(api_key)
    return json.dumps(db.search(query, limit), indent=2, default=str)

@mcp.tool()
def create_project(name: str, owner: str, status: str = "planning", stack: str = "", budget_usd: int = 0, deadline: str = "", api_key: str = "") -> str:
    """Create project with validation. Auth required if MCP_API_KEY set."""
    check_auth(api_key)
    # Pydantic validation
    validated = CreateProjectInput(name=name, owner=owner, status=status, stack=stack, budget_usd=budget_usd, deadline=deadline or None)
    proj_dict = {
        "name": validated.name,
        "owner": validated.owner,
        "status": validated.status,
        "stack": [s.strip() for s in validated.stack.split(",") if s.strip()],
        "budget_usd": validated.budget_usd,
        "deadline": validated.deadline
    }
    created = db.create(proj_dict)
    return json.dumps({"created": created}, indent=2, default=str)

@mcp.tool()
def update_project_status(project_id: str, new_status: str, api_key: str = "") -> str:
    """Update status: planning, active, in_progress, done, archived."""
    check_auth(api_key)
    if new_status not in ("planning","active","in_progress","done","archived"):
        return json.dumps({"error": f"Invalid status {new_status}"})
    updated = db.update_status(project_id, new_status)
    if not updated:
        return json.dumps({"error": "not found"})
    return json.dumps({"updated": updated}, indent=2, default=str)

@mcp.tool()
def delete_project(project_id: str, api_key: str = "") -> str:
    """Delete a project (dangerous, requires auth)."""
    check_auth(api_key)
    if not API_KEY:
        return json.dumps({"error": "Delete requires MCP_API_KEY to be set for safety"})
    if db.use_postgres:
        with db.pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM projects WHERE id=%s", (project_id,))
                conn.commit()
                return json.dumps({"deleted": project_id, "rows": cur.rowcount})
    else:
        data = db._load_json()
        before = len(data["projects"])
        data["projects"] = [p for p in data["projects"] if p["id"]!=project_id]
        db._save_json(data)
        return json.dumps({"deleted": project_id, "before": before, "after": len(data["projects"])})

@mcp.tool()
def analytics_dashboard(api_key: str = "") -> str:
    """Full analytics: by_status, by_owner, total_budget, overdue. Use for reports."""
    check_auth(api_key)
    return json.dumps(db.analytics(), indent=2, default=str)

@mcp.tool()
def budget_summary(api_key: str = "") -> str:
    """Quick budget summary."""
    check_auth(api_key)
    a = db.analytics()
    return json.dumps({"total_budget": a.get("total_budget"), "by_owner": a.get("by_owner"), "by_status": a.get("by_status")}, indent=2, default=str)

@mcp.tool()
def overdue_projects(api_key: str = "") -> str:
    """List projects past deadline and not done."""
    check_auth(api_key)
    if db.use_postgres:
        with db.pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id,name,deadline,status,owner FROM projects WHERE deadline < CURRENT_DATE AND status NOT IN ('done','archived')")
                cols = [d[0] for d in cur.description]
                return json.dumps([dict(zip(cols, r)) for r in cur.fetchall()], indent=2, default=str)
    else:
        today = datetime.date.today().isoformat()
        overdue = [p for p in db._load_json()["projects"] if p.get("deadline") and p["deadline"] < today and p["status"] not in ("done","archived")]
        return json.dumps(overdue, indent=2, default=str)

# ============ Prompts ============
@mcp.prompt()
def project_status_report() -> str:
    db_data = db.list(limit=100)
    analytics = db.analytics()
    return f"""You are a project manager. Data:

Projects: {json.dumps(db_data, indent=2, default=str)}

Analytics: {json.dumps(analytics, indent=2, default=str)}

Create:
1. Markdown table ID | Name | Status | Owner | Budget | Deadline
2. 3 risks (overdue, high budget in planning, owner overloaded)
3. Budget insights from analytics
4. Recommended next 3 actions
"""

@mcp.prompt()
def budget_review() -> str:
    return f"""Review budgets using:

{json.dumps(db.analytics(), indent=2, default=str)}

Identify overspend, underutilized budgets, and suggest reallocations.
"""

if __name__ == "__main__":
    mcp.run()
