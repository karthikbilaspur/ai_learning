
import structlog
from typing import List, Dict
import os

logger = structlog.get_logger()

# ---- YOUR ORIGINAL LOGIC (refactored for production) ----
try:
    import praw
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # ensure lexicon
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    sia = None

def get_reddit_client():
    from ...config import settings
    if not settings.REDDIT_CLIENT_ID:
        raise ValueError("Reddit credentials not set in .env")
    return praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent="task_python agent"
    )

def analyze_sentiment(subreddit_name: str, num_posts: int, analysis_type: str):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=num_posts)

    positive_count = negative_count = neutral_count = total = 0
    details = []

    for post in posts:
        text = post.title if analysis_type == "title" else post.selftext
        if not HAS_NLTK:
            sentiment = {"compound": 0}
        else:
            sentiment = sia.polarity_scores(text)
        compound = sentiment['compound']
        label = "neutral"
        if compound > 0.05:
            positive_count += 1; label = "positive"
        elif compound < -0.05:
            negative_count += 1; label = "negative"
        else:
            neutral_count += 1
        total += 1
        details.append({"title": post.title[:120], "compound": compound, "label": label})

    if total == 0:
        return {"message": "No posts found", "total": 0}

    return {
        "subreddit": subreddit_name,
        "total": total,
        "positive_pct": round((positive_count/total)*100,2),
        "negative_pct": round((negative_count/total)*100,2),
        "neutral_pct": round((neutral_count/total)*100,2),
        "details": details[:20]
    }

def analyze_comments(subreddit_name: str, num_posts: int):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=num_posts)
    pos = neg = neu = total = 0
    for post in posts:
        post.comments.replace_more(limit=0)
        for comment in post.comments.list()[:100]:
            if not HAS_NLTK:
                continue
            sentiment = sia.polarity_scores(comment.body)
            c = sentiment['compound']
            if c > 0.05: pos+=1
            elif c < -0.05: neg+=1
            else: neu+=1
            total+=1
    if total == 0:
        return {"message": "No comments"}
    return {
        "subreddit": subreddit_name,
        "total_comments": total,
        "positive_pct": round((pos/total)*100,2),
        "negative_pct": round((neg/total)*100,2),
        "neutral_pct": round((neu/total)*100,2)
    }

def compare_subreddits(subreddit_names: List[str], num_posts: int):
    results = {}
    for name in subreddit_names:
        results[name] = analyze_sentiment(name, num_posts, "title")
    return results

# ---- AGENT WRAPPER ----
def run(params: dict):
    logger.info("tool_start", tool="reddit_analysis", params=params)
    mode = params.get("mode", "sentiment") # sentiment | comments | compare
    if mode == "sentiment":
        return analyze_sentiment(params.get("subreddit","python"), int(params.get("num_posts",10)), params.get("analysis_type","title"))
    elif mode == "comments":
        return analyze_comments(params.get("subreddit","python"), int(params.get("num_posts",5)))
    elif mode == "compare":
        return compare_subreddits(params.get("subreddits",["python","programming"]), int(params.get("num_posts",5)))
    else:
        raise ValueError("Invalid mode")
