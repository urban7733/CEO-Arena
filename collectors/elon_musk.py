from scraper import BlogScraper, TranscriptScraper, TwitterScraper, PDFScraper

SPEAKER = "elon_musk"

# Public transcript and interview URLs
TRANSCRIPTS = [
    {
        "url": "https://lexfridman.com/elon-musk-4-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #400 - Elon Musk: War, AI, Aliens, Politics, Physics, Video Games, and Humanity",
        "interviewer": "Lex Fridman",
        "date": "2023-12-28",
    },
    {
        "url": "https://lexfridman.com/elon-musk-3-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #252 - Elon Musk: SpaceX, Mars, Tesla Autopilot, Self-Driving, Robotics, and AI",
        "interviewer": "Lex Fridman",
        "date": "2023-11-09",
    },
    {
        "url": "https://lexfridman.com/elon-musk-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #49 - Elon Musk: Neuralink, AI, Autopilot, and the Pale Blue Dot",
        "interviewer": "Lex Fridman",
        "date": "2019-11-12",
    },
    {
        "url": "https://lexfridman.com/elon-musk-2-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #252 - Elon Musk: SpaceX, Mars, Tesla, AI",
        "interviewer": "Lex Fridman",
        "date": "2021-12-28",
    },
    {
        "url": "https://singjupost.com/elon-musk-interview-with-don-lemon-full-transcript/",
        "source": "don_lemon_interview",
        "title": "Elon Musk Interview with Don Lemon - Full Transcript",
        "interviewer": "Don Lemon",
        "date": "2024-03-14",
    },
]

BLOG_POSTS = [
    {
        "url": "https://www.tesla.com/blog",
        "source": "tesla_blog",
    },
]

TWITTER_HANDLE = "elonmusk"


def collect_elon_musk():
    print("\n=== Collecting data for ELON MUSK ===\n")
    all_docs = []

    # 1. Transcripts
    print("[1/3] Scraping transcripts...")
    ts = TranscriptScraper(SPEAKER)
    for t in TRANSCRIPTS:
        doc = ts.scrape_transcript(
            url=t["url"],
            source=t["source"],
            title=t["title"],
            date=t.get("date", ""),
            interviewer=t.get("interviewer", ""),
        )
        if doc:
            all_docs.append(doc)

    # 2. Twitter
    print("[2/3] Fetching tweets...")
    tw = TwitterScraper(SPEAKER)
    tweets = tw.fetch_tweets(TWITTER_HANDLE, max_results=100)
    all_docs.extend(tweets)

    # 3. Blog posts
    print("[3/3] Scraping blogs...")
    bs = BlogScraper(SPEAKER)
    for b in BLOG_POSTS:
        docs = bs.scrape_blog_index(b["url"], source=b["source"])
        all_docs.extend(docs)

    print(f"\n  [DONE] Elon Musk: {len(all_docs)} documents collected\n")
    return all_docs
