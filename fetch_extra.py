#!/usr/bin/env python3
"""
Extra fetch: YC content, Joe Rogan transcripts, and company sites.
Budget: ~$3 remaining from Exa ($15 total, ~$7 used)
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

EXA_API_KEY = os.getenv("EXA_API_KEY")
EXA_URL = "https://api.exa.ai/search"
RAW_DIR = Path("data/raw")

SEARCH_COUNT = 0
MAX_SEARCHES = 25  # ~$2.50, staying under budget


def exa_search(query: str, num_results: int = 5) -> list[dict]:
    global SEARCH_COUNT
    if SEARCH_COUNT >= MAX_SEARCHES:
        print(f"  [BUDGET] Max searches reached ({MAX_SEARCHES})")
        return []

    headers = {
        "x-api-key": EXA_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "numResults": num_results,
        "contents": {"text": {"maxCharacters": 5000}},
        "type": "auto",
    }

    try:
        resp = requests.post(EXA_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        SEARCH_COUNT += 1
        print(f"  [EXA #{SEARCH_COUNT}] {query[:60]}...")
        time.sleep(0.5)
        return resp.json().get("results", [])
    except requests.RequestException as e:
        print(f"  [ERROR] Exa: {e}")
        return []


def save_result(speaker: str, result: dict, source: str, doc_type: str):
    text = result.get("text", "")
    if not text or len(text) < 200:
        return

    doc = {
        "id": f"{speaker[:2]}-extra-{SEARCH_COUNT}-{hash(result.get('url', '')) % 10000}",
        "speaker": speaker,
        "source": source,
        "source_url": result.get("url", ""),
        "date": (result.get("publishedDate", "") or "")[:10],
        "type": doc_type,
        "title": result.get("title", ""),
        "content": text,
        "metadata": {"exa_score": result.get("score", 0), "source_method": "exa_extra"},
    }

    out_dir = RAW_DIR / speaker
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"extra_{doc_type}_{abs(hash(result.get('url', ''))) % 100000}.json"
    with open(out_dir / filename, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"    [SAVED] {filename} ({len(text)} chars)")


def fetch_yc_content():
    """Y Combinator content about the CEOs"""
    print("\n=== Y COMBINATOR CONTENT ===")

    # Sam Altman was YC president - tons of content
    queries_altman = [
        ("Sam Altman Y Combinator startup school lecture transcript advice", "sam_altman", "lecture"),
        ("Sam Altman YC how to start a startup lecture Stanford transcript", "sam_altman", "lecture"),
        ("Sam Altman Y Combinator president interview what he learned", "sam_altman", "interview"),
    ]

    # Elon Musk at YC events
    queries_musk = [
        ("Elon Musk Y Combinator interview startup advice transcript", "elon_musk", "interview"),
        ("Elon Musk YC startup school talk how to build companies", "elon_musk", "interview"),
    ]

    # Zuckerberg at YC/startup events
    queries_zuck = [
        ("Mark Zuckerberg Y Combinator startup school interview transcript", "mark_zuckerberg", "interview"),
        ("Mark Zuckerberg startup advice how he built Facebook early days", "mark_zuckerberg", "interview"),
    ]

    for query, speaker, doc_type in queries_altman + queries_musk + queries_zuck:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "yc_content", doc_type)


def fetch_joe_rogan():
    """Joe Rogan interviews with all 4 CEOs"""
    print("\n=== JOE ROGAN INTERVIEWS ===")

    queries = [
        ("Elon Musk Joe Rogan Experience full transcript conversation smoking weed", "elon_musk"),
        ("Elon Musk Joe Rogan podcast transcript AI SpaceX Neuralink 2023 2024", "elon_musk"),
        ("Mark Zuckerberg Joe Rogan Experience full transcript MMA Meta AI", "mark_zuckerberg"),
        ("Mark Zuckerberg Joe Rogan podcast transcript metaverse open source", "mark_zuckerberg"),
        ("Sam Altman Joe Rogan podcast interview transcript OpenAI", "sam_altman"),
    ]

    for query, speaker in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "joe_rogan_podcast", "interview")


def fetch_company_sites():
    """Content directly from company sites: xAI, Meta AI, Anthropic, OpenAI"""
    print("\n=== COMPANY SITES ===")

    queries = [
        # xAI / Grok
        ("site:x.ai Grok AI announcement blog post xAI mission", "elon_musk", "blog"),
        ("xAI Grok model release announcement capabilities open source", "elon_musk", "blog"),
        ("Elon Musk xAI company mission statement why he started xAI", "elon_musk", "article"),

        # OpenAI
        ("site:openai.com blog Sam Altman announcement GPT release", "sam_altman", "blog"),
        ("OpenAI blog post Sam Altman planning for AGI safety", "sam_altman", "blog"),
        ("OpenAI official blog ChatGPT launch announcement Sam Altman", "sam_altman", "blog"),

        # Anthropic
        ("site:anthropic.com blog Dario Amodei Claude announcement", "dario_amodei", "blog"),
        ("Anthropic blog responsible scaling policy Claude safety", "dario_amodei", "blog"),

        # Meta AI
        ("site:ai.meta.com blog Mark Zuckerberg Llama release announcement", "mark_zuckerberg", "blog"),
        ("Meta AI blog Llama 3 open source release Zuckerberg", "mark_zuckerberg", "blog"),
    ]

    for query, speaker, doc_type in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "company_site", doc_type)


if __name__ == "__main__":
    if not EXA_API_KEY:
        print("ERROR: EXA_API_KEY not set in .env")
        exit(1)

    print(f"Starting extra content fetch (max {MAX_SEARCHES} searches)")
    print(f"Estimated cost: ~${MAX_SEARCHES * 0.10:.2f}\n")

    fetch_yc_content()
    fetch_joe_rogan()
    fetch_company_sites()

    print(f"\n{'='*50}")
    print(f"DONE! Extra searches: {SEARCH_COUNT}")
    print(f"Estimated cost: ~${SEARCH_COUNT * 0.10:.2f}")
    print(f"Total Exa spend: ~${7 + SEARCH_COUNT * 0.10:.2f} of $15")
    print(f"{'='*50}")
