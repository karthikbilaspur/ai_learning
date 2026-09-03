
# Standalone runner for restaurant_mgmt - no Docker, no Auth needed
import sys
sys.path.append('..')
from src.agent.tools.restaurant_mgmt import run, *  # your original logic is inside

if __name__ == "__main__":
    import json
    # Example: python standalone/run_restaurant_mgmt.py '{"subreddit":"python","num_posts":5}'
    params = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
    print(run(params))
