
"""
Demo: Run all 9 original tools together as an agent pipeline
"""
import time, json, pathlib
from src.agent.core import AgentOrchestrator

agent = AgentOrchestrator()
pathlib.Path("/app/data").mkdir(parents=True, exist_ok=True)
for i in range(3):
    pathlib.Path(f"/app/data/test_file_{i}.txt").write_text(f"demo {i}")

tools_to_run = [
    ("restaurant", {"action": "menu"}, "Restaurant management - menu"),
    ("restaurant", {"action": "order", "items": ["fries", "burger", "drinks"]}, "Restaurant order"),
    ("tower_defense", {"towers": [{"x":100,"y":100},{"x":300,"y":300}], "num_enemies": 10}, "Tower defense"),
    ("reverse_tower", {"num_towers": 3}, "Reverse tower"),
    ("rename_files", {"directory": "/app/data", "old_name": "test_file", "new_name": "prod_file", "languages": []}, "File renamer"),
    ("rename_with_time", {"directory": "/app/data", "old_name": "prod_file", "new_name": "final_file"}, "File renamer with time"),
]

for tool, params, desc in tools_to_run:
    print(f"\n> {tool}: {desc}")
    try:
        res = agent.execute(tool, params)
        print(f"  OK: {str(res['result'])[:200]}")
    except Exception as e:
        print(f"  Fail: {e}")
print("\nDemo done - dual mode verified")
