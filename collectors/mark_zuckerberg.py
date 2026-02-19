from scraper import BlogScraper, TranscriptScraper, TwitterScraper, PDFScraper

SPEAKER = "mark_zuckerberg"

TRANSCRIPTS = [
    {
        "url": "https://lexfridman.com/mark-zuckerberg-3-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #383 - Mark Zuckerberg: First Interview in the Metaverse",
        "interviewer": "Lex Fridman",
        "date": "2023-06-09",
    },
    {
        "url": "https://lexfridman.com/mark-zuckerberg-2-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #267 - Mark Zuckerberg: Meta, Facebook, Instagram, and the Metaverse",
        "interviewer": "Lex Fridman",
        "date": "2022-02-24",
    },
    {
        "url": "https://singjupost.com/mark-zuckerberg-on-joe-rogan-experience-full-transcript/",
        "source": "joe_rogan_podcast",
        "title": "Mark Zuckerberg on Joe Rogan Experience - Full Transcript",
        "interviewer": "Joe Rogan",
        "date": "2024-06-27",
    },
]

# Zuckerberg Files - Marquette University Archive (public transcripts)
ZUCKERBERG_FILES_BASE = "https://epublications.marquette.edu/zuckerberg_files_transcripts"

BLOG_URLS = [
    "https://about.fb.com/news/2024/07/open-source-ai-is-the-path-forward/",
    "https://about.fb.com/news/2024/01/mark-zuckerberg-2024-vision/",
]

KEY_SPEECHES = [
    {
        "url": "https://about.fb.com/news/2017/05/transcript-mark-zuckerberg-harvard-commencement/",
        "source": "harvard_speech",
        "title": "Mark Zuckerberg Harvard Commencement Address",
        "date": "2017-05-25",
    },
]

TWITTER_HANDLE = "finkd"


def collect_mark_zuckerberg():
    print("\n=== Collecting data for MARK ZUCKERBERG ===\n")
    all_docs = []

    # 1. Key speeches
    print("[1/5] Scraping key speeches...")
    ts = TranscriptScraper(SPEAKER)
    for s in KEY_SPEECHES:
        doc = ts.scrape_transcript(
            url=s["url"],
            source=s["source"],
            title=s["title"],
            date=s.get("date", ""),
        )
        if doc:
            all_docs.append(doc)

    # 2. Transcripts/Interviews
    print("[2/5] Scraping interview transcripts...")
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

    # 3. Blog posts
    print("[3/5] Scraping blog posts...")
    bs = BlogScraper(SPEAKER)
    for url in BLOG_URLS:
        title = url.split("/")[-1].replace("-", " ").title()
        doc = bs.scrape_blog_post(url, source="meta_blog", title=title)
        if doc:
            all_docs.append(doc)

    # 4. Zuckerberg Files index
    print("[4/5] Checking Zuckerberg Files archive...")
    zf_docs = bs.scrape_blog_index(
        ZUCKERBERG_FILES_BASE,
        source="zuckerberg_files",
        link_selector="a[href*='zuckerberg_files']",
    )
    all_docs.extend(zf_docs)

    # 5. Twitter
    print("[5/5] Fetching tweets...")
    tw = TwitterScraper(SPEAKER)
    tweets = tw.fetch_tweets(TWITTER_HANDLE, max_results=100)
    all_docs.extend(tweets)

    print(f"\n  [DONE] Mark Zuckerberg: {len(all_docs)} documents collected\n")
    return all_docs
