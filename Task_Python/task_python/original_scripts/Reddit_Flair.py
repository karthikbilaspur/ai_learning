import praw

# Reddit API credentials
reddit = praw.Reddit(client_id="YOUR_CLIENT_ID",
                     client_secret="YOUR_CLIENT_SECRET",
                     user_agent="Flair Detector")

def get_flair(subreddit_name: str, username: str) -> str:
    try:
        subreddit = reddit.subreddit(subreddit_name)
        user = reddit.redditor(username)
        flair = user.flair(subreddit)
        if flair:
            return flair
        else:
            return "No flair found"
    except praw.exceptions.RedditorNotFound:
        return "User not found"
    except Exception as e:
        return f"Error getting flair: {e}"

def get_user_flairs(username: str) -> dict[str, str]:
    try:
        user = reddit.redditor(username)
        flairs = {}
        for subreddit in user.moderated():
            flair = user.flair(subreddit)
            if flair:
                flairs[subreddit.display_name] = flair
        return flairs
    except praw.exceptions.RedditorNotFound:
        return "User not found"
    except Exception as e:
        return f"Error getting flairs: {e}"

def main():
    while True:
        print("\n1. Get flair for a user in a subreddit")
        print("2. Get all flairs for a user")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            subreddit_name = input("Enter the subreddit name: ")
            username = input("Enter the username: ")
            flair = get_flair(subreddit_name, username)
            print(f"Flair: {flair}")
        elif choice == "2":
            username = input("Enter the username: ")
            flairs = get_user_flairs(username)
            if isinstance(flairs, dict):
                for subreddit, flair in flairs.items():
                    print(f"Subreddit: {subreddit}, Flair: {flair}")
            else:
                print(flairs)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()