
import structlog
logger = structlog.get_logger()
def run_reverse(params: dict):
    logger.info("tool_start", tool="reverse_tower")
    n = int(params.get("n", 5))
    pattern = "\n".join([" ".join([str(j) for j in range(i,0,-1)]) for i in range(n,0,-1)])
    return {"pattern": "reverse_tower", "n": n, "output": pattern}

def run_defense(params: dict):
    logger.info("tool_start", tool="tower_defense")
    # Original game logic: tower defense simulation
    towers = params.get("towers", 3)
    enemies = params.get("enemies", 10)
    # simple simulation
    score = max(0, towers*10 - enemies)
    return {"game": "tower_defense", "towers": towers, "enemies": enemies, "score": score, "status": "simulated - connect pygame for full UI"}
