from scraper import BlogScraper, TranscriptScraper, TwitterScraper

SPEAKER = "dario_amodei"

TRANSCRIPTS = [
    {
        "url": "https://lexfridman.com/dario-amodei-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #452 - Dario Amodei: Anthropic CEO on Claude, AGI & the Future of AI & Humanity",
        "interviewer": "Lex Fridman",
        "date": "2024-10-14",
    },
    {
        "url": "https://singjupost.com/transcript-anthropic-ceo-dario-amodeis-interview/",
        "source": "singjupost_transcript",
        "title": "Anthropic CEO Dario Amodei Interview Transcript",
        "interviewer": "",
        "date": "2024-02-01",
    },
    {
        "url": "https://www.dwarkeshpatel.com/p/dario-amodei",
        "source": "dwarkesh_podcast",
        "title": "Dwarkesh Podcast - Dario Amodei: Scaling, Alignment, and the Future of Humanity",
        "interviewer": "Dwarkesh Patel",
        "date": "2024-03-20",
    },
]

ESSAYS = [
    {
        "url": "https://darioamodei.com/machines-of-loving-grace",
        "source": "darioamodei_blog",
        "title": "Machines of Loving Grace - How AI Could Transform the World for the Better",
        "date": "2024-10-01",
    },
]

ANTHROPIC_BLOG_URLS = [
    "https://www.anthropic.com/research/core-views-on-ai-safety",
    "https://www.anthropic.com/news/the-anthropic-model-spec",
    "https://www.anthropic.com/news/reflections-on-our-responsible-scaling-policy",
]

TWITTER_HANDLE = "DarioAmodei"


def collect_dario_amodei():
    print("\n=== Collecting data for DARIO AMODEI ===\n")
    all_docs = []

    # 1. Essays
    print("[1/4] Scraping essays...")
    bs = BlogScraper(SPEAKER)
    for e in ESSAYS:
        doc = bs.scrape_blog_post(
            url=e["url"],
            source=e["source"],
            title=e["title"],
            date=e.get("date", ""),
        )
        if doc:
            all_docs.append(doc)

    # 2. Anthropic blog posts
    print("[2/4] Scraping Anthropic blog...")
    for url in ANTHROPIC_BLOG_URLS:
        title = url.split("/")[-1].replace("-", " ").title()
        doc = bs.scrape_blog_post(url, source="anthropic_blog", title=title)
        if doc:
            all_docs.append(doc)

    # 3. Transcripts
    print("[3/4] Scraping transcripts...")
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

    # 4. Twitter
    print("[4/4] Fetching tweets...")
    tw = TwitterScraper(SPEAKER)
    tweets = tw.fetch_tweets(TWITTER_HANDLE, max_results=100)
    all_docs.extend(tweets)

    print(f"\n  [DONE] Dario Amodei: {len(all_docs)} documents collected\n")
    return all_docs
