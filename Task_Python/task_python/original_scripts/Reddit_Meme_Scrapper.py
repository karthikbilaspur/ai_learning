import praw
import requests
import os
import concurrent.futures
from PIL import Image
from io import BytesIO

# Reddit API credentials
reddit = praw.Reddit(client_id="YOUR_CLIENT_ID",
                     client_secret="YOUR_CLIENT_SECRET",
                     user_agent="Meme Scraper")

def scrape_memes(subreddit_name: str, num_posts: int) -> list[dict[str, str]]:
    try:
        subreddit = reddit.subreddit(subreddit_name)
        memes = []

        for post in subreddit.hot(limit=num_posts):
            if post.url.endswith(('.jpg', '.png', '.gif')):
                memes.append({
                    'title': post.title,
                    'url': post.url
                })

        return memes
    except Exception as e:
        print(f"Error scraping memes: {e}")
        return []

def download_meme(meme: dict[str, str]):
    try:
        response = requests.get(meme['url'])
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.verify()
            with open(f"memes/{meme['title']}.jpg", 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {meme['title']}")
        else:
            print(f"Failed to download {meme['title']}")
    except Exception as e:
        print(f"Error downloading {meme['title']}: {e}")

def download_memes(memes: list[dict[str, str]]):
    if not os.path.exists('memes'):
        os.makedirs('memes')

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_meme, memes)

def main():
    subreddit_name = input("Enter the subreddit name: ")
    num_posts = int(input("Enter the number of posts to scrape: "))

    memes = scrape_memes(subreddit_name, num_posts)
    download_memes(memes)

if __name__ == "__main__":
    main()