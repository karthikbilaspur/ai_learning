
import structlog
logger = structlog.get_logger()

def get_reddit_client():
    from ...config import settings
    import praw
    if not settings.REDDIT_CLIENT_ID:
        raise ValueError("Reddit credentials not set in .env")
    return praw.Reddit(client_id=settings.REDDIT_CLIENT_ID, client_secret=settings.REDDIT_CLIENT_SECRET, user_agent="task_python")

def get_flair(subreddit_name: str, username: str) -> str:
    import praw
    reddit = get_reddit_client()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        user = reddit.redditor(username)
        flair = user.flair(subreddit)
        return flair if flair else "No flair found"
    except praw.exceptions.RedditorNotFound:
        return "User not found"
    except Exception as e:
        logger.error("flair_error", error=str(e))
        return f"Error getting flair: {e}"

def get_user_flairs(username: str):
    import praw
    reddit = get_reddit_client()
    try:
        user = reddit.redditor(username)
        flairs = {}
        for subreddit in user.moderated():
            flair = user.flair(subreddit)
            if flair:
                flairs[subreddit.display_name] = flair
        return flairs
    except praw.exceptions.RedditorNotFound:
        return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}

def run(params: dict):
    logger.info("tool_start", tool="reddit_flair", params=params)
    mode = params.get("mode", "single")
    if mode == "single":
        return {"flair": get_flair(params.get("subreddit","python"), params.get("username","spez"))}
    else:
        return get_user_flairs(params.get("username","spez"))
