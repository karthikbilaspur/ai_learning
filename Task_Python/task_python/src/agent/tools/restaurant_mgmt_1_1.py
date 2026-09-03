
import structlog
from sqlalchemy.orm import Session

logger = structlog.get_logger()

# In-memory demo, migrated to DB in prod
MENU = {"pizza": 12.5, "burger": 8.0, "pasta": 10.0}

def run(params: dict, db: Session = None):
    logger.info("tool_start", tool="restaurant_mgmt", params=params)
    action = params.get("action", "menu")
    if action == "menu":
        return {"menu": MENU}
    if action == "order":
        items = params.get("items", [])
        total = sum(MENU.get(i,0) for i in items)
        # would save order to DB: TaskLog or Order table
        return {"items": items, "total": total, "status": "order placed"}
    return {"error": "unknown action"}
