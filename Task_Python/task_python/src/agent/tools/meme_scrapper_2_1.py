
import structlog, os, pathlib, concurrent.futures, requests
from io import BytesIO
from PIL import Image

logger = structlog.get_logger()
ALLOWED_MEME_DIR = pathlib.Path("/app/data/memes")
ALLOWED_MEME_DIR.mkdir(parents=True, exist_ok=True)

def get_reddit_client():
    from ...config import settings
    import praw
    if not settings.REDDIT_CLIENT_ID:
        raise ValueError("Reddit credentials not set")
    return praw.Reddit(client_id=settings.REDDIT_CLIENT_ID, client_secret=settings.REDDIT_CLIENT_SECRET, user_agent="Meme Scraper")

def scrape_memes(subreddit_name: str, num_posts: int):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    memes = []
    for post in subreddit.hot(limit=num_posts):
        if post.url.endswith(('.jpg','.png','.gif','.jpeg')):
            memes.append({'title': post.title, 'url': post.url})
    return memes

def download_meme(meme: dict):
    try:
        response = requests.get(meme['url'], timeout=10)
        if response.status_code == 200:
            # validate image
            Image.open(BytesIO(response.content)).verify()
            safe_title = "".join(c for c in meme['title'] if c.isalnum() or c in (' ','_','-')).strip()[:50]
            path = ALLOWED_MEME_DIR / f"{safe_title}.jpg"
            with open(path, 'wb') as f:
                f.write(response.content)
            return str(path)
    except Exception as e:
        logger.warning("meme_download_failed", title=meme.get('title'), error=str(e))
        return None

def run(params: dict):
    logger.info("tool_start", tool="meme_scrapper", params=params)
    subreddit = params.get("subreddit","memes")
    num = int(params.get("num_posts",5))
    memes = scrape_memes(subreddit, num)
    if params.get("download", False):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            paths = list(executor.map(download_meme, memes))
        return {"scraped": len(memes), "downloaded": [p for p in paths if p], "memes": memes}
    return {"scraped": len(memes), "memes": memes}
