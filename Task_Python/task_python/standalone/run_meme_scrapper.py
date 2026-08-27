
# Standalone runner for meme_scrapper - no Docker, no Auth needed
import sys
sys.path.append('..')
from src.agent.tools.meme_scrapper import run, *  # your original logic is inside

if __name__ == "__main__":
    import json
    # Example: python standalone/run_meme_scrapper.py '{"subreddit":"python","num_posts":5}'
    params = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
    print(run(params))
