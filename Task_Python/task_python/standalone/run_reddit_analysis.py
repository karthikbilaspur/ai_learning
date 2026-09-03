
# Standalone runner for reddit_analysis - no Docker, no Auth needed
import sys
sys.path.append('..')
from src.agent.tools.reddit_analysis import run, *  # your original logic is inside

if __name__ == "__main__":
    import json
    # Example: python standalone/run_reddit_analysis.py '{"subreddit":"python","num_posts":5}'
    params = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
    print(run(params))
