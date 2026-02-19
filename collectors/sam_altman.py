from scraper import BlogScraper, TranscriptScraper, TwitterScraper, PDFScraper

SPEAKER = "sam_altman"

TRANSCRIPTS = [
    {
        "url": "https://lexfridman.com/sam-altman-2-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #367 - Sam Altman: OpenAI CEO on GPT-4, ChatGPT, and the Future of AI",
        "interviewer": "Lex Fridman",
        "date": "2023-03-25",
    },
    {
        "url": "https://lexfridman.com/sam-altman-transcript",
        "source": "lex_fridman_podcast",
        "title": "Lex Fridman #205 - Sam Altman: OpenAI CEO on GPT and the Future of AI",
        "interviewer": "Lex Fridman",
        "date": "2021-07-21",
    },
    {
        "url": "https://singjupost.com/transcript-openai-ceo-sam-altmans-interview/",
        "source": "singjupost_transcript",
        "title": "OpenAI CEO Sam Altman Interview Transcript",
        "interviewer": "",
        "date": "2024-01-15",
    },
    {
        "url": "https://www.ted.com/talks/sam_altman_what_to_expect_as_ai_changes_everything/transcript",
        "source": "ted_talk",
        "title": "Sam Altman: What to expect as AI changes everything",
        "interviewer": "",
        "date": "2024-04-15",
    },
]

BLOG_URLS = [
    "https://blog.samaltman.com/what-i-wish-someone-had-told-me",
    "https://blog.samaltman.com/the-intelligence-age",
    "https://blog.samaltman.com/reflections",
    "https://blog.samaltman.com/moore-s-law-for-everything",
    "https://blog.samaltman.com/how-to-be-successful",
    "https://blog.samaltman.com/the-merge",
    "https://blog.samaltman.com/productivity",
    "https://blog.samaltman.com/advice-for-ambitious-19-year-olds",
    "https://blog.samaltman.com/idea-generation",
    "https://blog.samaltman.com/researchers-and-founders",
]

PDFS = [
    {
        "url": "https://www.judiciary.senate.gov/imo/media/doc/2023-05-16%20-%20Bio%20&%20Testimony%20-%20Altman.pdf",
        "source": "senate_testimony",
        "title": "Sam Altman Senate Judiciary Testimony on AI Oversight",
        "date": "2023-05-16",
    },
]

TWITTER_HANDLE = "sama"


def collect_sam_altman():
    print("\n=== Collecting data for SAM ALTMAN ===\n")
    all_docs = []

    # 1. Blog posts
    print("[1/4] Scraping blog posts...")
    bs = BlogScraper(SPEAKER)
    for url in BLOG_URLS:
        title = url.split("/")[-1].replace("-", " ").title()
        doc = bs.scrape_blog_post(url, source="samaltman_blog", title=title)
        if doc:
            all_docs.append(doc)

    # 2. Transcripts
    print("[2/4] Scraping transcripts...")
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

    # 3. PDFs
    print("[3/4] Downloading PDFs...")
    ps = PDFScraper(SPEAKER)
    for p in PDFS:
        doc = ps.download_and_extract(
            url=p["url"],
            source=p["source"],
            title=p["title"],
            date=p.get("date", ""),
        )
        if doc:
            all_docs.append(doc)

    # 4. Twitter
    print("[4/4] Fetching tweets...")
    tw = TwitterScraper(SPEAKER)
    tweets = tw.fetch_tweets(TWITTER_HANDLE, max_results=100)
    all_docs.extend(tweets)

    print(f"\n  [DONE] Sam Altman: {len(all_docs)} documents collected\n")
    return all_docs
