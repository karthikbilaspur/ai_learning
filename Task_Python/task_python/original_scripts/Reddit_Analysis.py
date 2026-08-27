import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Reddit API credentials
reddit = praw.Reddit(client_id="YOUR_CLIENT_ID",
                     client_secret="YOUR_CLIENT_SECRET",
                     user_agent="Sentiment Analysis")

# Initialize sentiment intensity analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(subreddit_name: str, num_posts: int, analysis_type: str):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=num_posts)

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total = 0

    for post in posts:
        if analysis_type == "title":
            sentiment = sia.polarity_scores(post.title)
        elif analysis_type == "selftext":
            sentiment = sia.polarity_scores(post.selftext)
        else:
            raise ValueError("Invalid analysis type")

        compound_score = sentiment['compound']

        if compound_score > 0.05:
            positive_count += 1
        elif compound_score < -0.05:
            negative_count += 1
        else:
            neutral_count += 1

        total += 1

    if total > 0:
        positive_percentage = (positive_count / total) * 100
        negative_percentage = (negative_count / total) * 100
        neutral_percentage = (neutral_count / total) * 100

        print(f"Subreddit: {subreddit_name}")
        print(f"Positive sentiment: {positive_percentage:.2f}%")
        print(f"Negative sentiment: {negative_percentage:.2f}%")
        print(f"Neutral sentiment: {neutral_percentage:.2f}%")
    else:
        print("No posts found.")

def analyze_comments(subreddit_name: str, num_posts: int):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=num_posts)

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total_comments = 0

    for post in posts:
        post.comments.replace_more(limit=None)
        for comment in post.comments.list():
            sentiment = sia.polarity_scores(comment.body)
            compound_score = sentiment['compound']

            if compound_score > 0.05:
                positive_count += 1
            elif compound_score < -0.05:
                negative_count += 1
            else:
                neutral_count += 1

            total_comments += 1

    if total_comments > 0:
        positive_percentage = (positive_count / total_comments) * 100
        negative_percentage = (negative_count / total_comments) * 100
        neutral_percentage = (neutral_count / total_comments) * 100

        print(f"Subreddit: {subreddit_name} (comments)")
        print(f"Positive sentiment: {positive_percentage:.2f}%")
        print(f"Negative sentiment: {negative_percentage:.2f}%")
        print(f"Neutral sentiment: {neutral_percentage:.2f}%")
    else:
        print("No comments found.")

def compare_subreddits(subreddit_names: list[str], num_posts: int):
    for subreddit_name in subreddit_names:
        analyze_sentiment(subreddit_name, num_posts, "title")
        print("\n")

def main():
    nltk.download('vader_lexicon')

    while True:
        print("\nReddit Sentiment Analysis")
        print("1. Analyze sentiment of a subreddit")
        print("2. Analyze comments of a subreddit")
        print("3. Compare sentiment of multiple subreddits")
        print("4. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            subreddit_name = input("Enter the subreddit name: ")
            num_posts = int(input("Enter the number of posts to analyze: "))
            print("\nAnalyze:")
            print("1. Post titles")
            print("2. Post selftext")
            analysis_type = input("Enter your choice: ")
            if analysis_type == "1":
                analyze_sentiment(subreddit_name, num_posts, "title")
            elif analysis_type == "2":
                analyze_sentiment(subreddit_name, num_posts, "selftext")
            else:
                print("Invalid choice.")
        elif choice == "2":
            subreddit_name = input("Enter the subreddit name: ")
            num_posts = int(input("Enter the number of posts to analyze: "))
            analyze_comments(subreddit_name, num_posts)
        elif choice == "3":
            subreddit_names = input("Enter the subreddit names (comma-separated): ").split(',')
            subreddit_names = [name.strip() for name in subreddit_names]
            num_posts = int(input("Enter the number of posts to analyze: "))
            compare_subreddits(subreddit_names, num_posts)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()