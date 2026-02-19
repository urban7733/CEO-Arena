import tweepy

from config import TWITTER_BEARER_TOKEN
from .base_scraper import BaseScraper


class TwitterScraper(BaseScraper):
    def __init__(self, speaker: str):
        super().__init__(speaker)
        if not TWITTER_BEARER_TOKEN:
            print("[WARN] TWITTER_BEARER_TOKEN not set in .env")
            self.client = None
        else:
            self.client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

    def fetch_tweets(self, username: str, max_results: int = 100) -> list[dict]:
        if not self.client:
            print("  [SKIP] Twitter client not initialized (missing API key)")
            return []

        try:
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"  [ERROR] User @{username} not found")
                return []

            user_id = user.data.id

            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "text"],
                exclude=["retweets", "replies"],
            )

            if not tweets.data:
                print(f"  [WARN] No tweets found for @{username}")
                return []

            docs = []
            for tweet in tweets.data:
                doc = self.make_document(
                    content=tweet.text,
                    source="twitter",
                    source_url=f"https://x.com/{username}/status/{tweet.id}",
                    doc_type="tweet",
                    title=f"Tweet by @{username}",
                    date=tweet.created_at.strftime("%Y-%m-%d") if tweet.created_at else "",
                    metadata={
                        "tweet_id": str(tweet.id),
                        "username": username,
                        "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
                    },
                )
                docs.append(doc)

            self.save_documents(docs)
            return docs

        except tweepy.TweepyException as e:
            print(f"  [ERROR] Twitter API error for @{username}: {e}")
            return []
