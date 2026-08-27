
import time, structlog
from typing import Dict, Any
from .tools import reddit_analysis, reddit_flair, meme_scrapper, file_tools, restaurant_mgmt, tower_defense

logger = structlog.get_logger()

TOOL_REGISTRY = {
    "reddit_analysis": reddit_analysis.run,
    "reddit_flair": reddit_flair.run,
    "meme_scrapper": meme_scrapper.run,
    "rename_files": file_tools.rename_files,
    "rename_with_time": file_tools.rename_with_time,
    "rescale_image": file_tools.rescale_image,
    "restaurant": restaurant_mgmt.run,
    "reverse_tower": tower_defense.run_reverse,
    "tower_defense": tower_defense.run_defense,
}

class AgentOrchestrator:
    def execute(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        if tool not in TOOL_REGISTRY:
            raise ValueError(f"Tool {tool} not found. Available: {list(TOOL_REGISTRY.keys())}")
        try:
            result = TOOL_REGISTRY[tool](params)
            duration = int((time.time()-start)*1000)
            logger.info("agent_execute", tool=tool, duration_ms=duration, status="success")
            return {"result": result, "duration_ms": duration, "status": "success"}
        except Exception as e:
            logger.error("agent_execute_failed", tool=tool, error=str(e))
            raise
