#!/usr/bin/env python3
"""
Fetch content for all 4 CEOs using Exa.ai semantic search.
Budget: max $10 of $15 Exa credit.
Each search with content costs ~$0.10, so we can do ~100 searches.
We'll be strategic: ~20-25 searches per CEO.
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
MAX_SEARCHES = 80  # Stay well under budget


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
        time.sleep(0.5)  # Rate limit
        return resp.json().get("results", [])
    except requests.RequestException as e:
        print(f"  [ERROR] Exa: {e}")
        return []


def save_result(speaker: str, result: dict, source: str, doc_type: str):
    text = result.get("text", "")
    if not text or len(text) < 200:
        return

    doc = {
        "id": f"{speaker[:2]}-exa-{SEARCH_COUNT}-{hash(result.get('url', '')) % 10000}",
        "speaker": speaker,
        "source": source,
        "source_url": result.get("url", ""),
        "date": (result.get("publishedDate", "") or "")[:10],
        "type": doc_type,
        "title": result.get("title", ""),
        "content": text,
        "metadata": {"exa_score": result.get("score", 0), "source_method": "exa_search"},
    }

    out_dir = RAW_DIR / speaker
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"exa_{doc_type}_{abs(hash(result.get('url', ''))) % 100000}.json"
    with open(out_dir / filename, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"    [SAVED] {filename} ({len(text)} chars)")


def fetch_elon_musk():
    print("\n=== EXA: ELON MUSK ===")
    speaker = "elon_musk"

    queries = [
        ("Elon Musk interview transcript about AI and xAI Grok", "interview"),
        ("Elon Musk interview transcript SpaceX Mars colonization", "interview"),
        ("Elon Musk interview transcript Tesla autonomous driving", "interview"),
        ("Elon Musk interview transcript Neuralink brain computer interface", "interview"),
        ("Elon Musk podcast full transcript 2024", "interview"),
        ("Elon Musk speech keynote transcript", "speech"),
        ("Elon Musk opinion on artificial intelligence safety regulation", "article"),
        ("Elon Musk views on free speech social media Twitter X", "article"),
        ("Elon Musk on population collapse demographics future", "article"),
        ("Elon Musk biography quotes first principles thinking", "article"),
        ("Elon Musk Joe Rogan podcast transcript", "interview"),
        ("Elon Musk Lex Fridman full conversation transcript", "interview"),
        ("Elon Musk DealBook Summit interview transcript", "interview"),
        ("Elon Musk All-In podcast interview transcript", "interview"),
        # Company culture, rules, innovation, motivation
        ("Elon Musk Tesla company culture management style hardcore", "article"),
        ("Elon Musk SpaceX engineering culture innovation process", "article"),
        ("Elon Musk management rules email employees productivity", "article"),
        ("Elon Musk motivation why he works what drives him purpose", "article"),
        ("Elon Musk tech stack engineering decisions first principles", "article"),
    ]

    for query, doc_type in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "exa_" + doc_type, doc_type)


def fetch_sam_altman():
    print("\n=== EXA: SAM ALTMAN ===")
    speaker = "sam_altman"

    queries = [
        ("Sam Altman interview transcript OpenAI GPT future of AI", "interview"),
        ("Sam Altman blog post personal essay", "blog"),
        ("Sam Altman podcast transcript AGI superintelligence", "interview"),
        ("Sam Altman Senate testimony AI regulation transcript", "testimony"),
        ("Sam Altman on startups venture capital Y Combinator advice", "article"),
        ("Sam Altman keynote speech transcript 2024", "speech"),
        ("Sam Altman interview about OpenAI board crisis fired", "interview"),
        ("Sam Altman views on universal basic income economic impact AI", "article"),
        ("Sam Altman Lex Fridman full conversation transcript", "interview"),
        ("Sam Altman All-In Summit interview transcript", "interview"),
        ("Sam Altman TED talk transcript AI humanity", "speech"),
        ("Sam Altman interview Acquired podcast transcript", "interview"),
        # Company culture, rules, innovation, motivation
        ("Sam Altman OpenAI company culture how they build ship fast", "article"),
        ("Sam Altman on innovation process how OpenAI develops products", "article"),
        ("Sam Altman motivation purpose why he runs OpenAI drives him", "article"),
        ("Sam Altman on hiring talent team building startup culture", "article"),
        ("OpenAI tech stack infrastructure engineering decisions", "article"),
    ]

    for query, doc_type in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "exa_" + doc_type, doc_type)


def fetch_dario_amodei():
    print("\n=== EXA: DARIO AMODEI ===")
    speaker = "dario_amodei"

    queries = [
        ("Dario Amodei interview transcript AI safety Anthropic Claude", "interview"),
        ("Dario Amodei essay blog post machines of loving grace", "essay"),
        ("Dario Amodei podcast transcript scaling laws alignment", "interview"),
        ("Dario Amodei Lex Fridman transcript full conversation", "interview"),
        ("Dario Amodei interview about AI existential risk", "interview"),
        ("Dario Amodei speech keynote transcript 2024", "speech"),
        ("Dario Amodei views on open source AI safety", "article"),
        ("Dario Amodei Ezra Klein interview transcript", "interview"),
        ("Dario Amodei 60 Minutes CBS interview transcript", "interview"),
        ("Dario Amodei Senate testimony AI policy transcript", "testimony"),
        ("Dario Amodei Dwarkesh Patel podcast transcript", "interview"),
        ("Anthropic CEO Dario Amodei on constitutional AI RLHF", "article"),
        # Company culture, rules, innovation, motivation
        ("Dario Amodei Anthropic company culture safety-first approach", "article"),
        ("Anthropic responsible scaling policy how they build AI safely", "article"),
        ("Dario Amodei motivation why he left OpenAI started Anthropic", "article"),
        ("Dario Amodei on innovation research process at Anthropic", "article"),
        ("Anthropic tech stack Claude training infrastructure decisions", "article"),
    ]

    for query, doc_type in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "exa_" + doc_type, doc_type)


def fetch_mark_zuckerberg():
    print("\n=== EXA: MARK ZUCKERBERG ===")
    speaker = "mark_zuckerberg"

    queries = [
        ("Mark Zuckerberg interview transcript open source AI Llama", "interview"),
        ("Mark Zuckerberg interview transcript metaverse VR AR", "interview"),
        ("Mark Zuckerberg podcast transcript 2024", "interview"),
        ("Mark Zuckerberg Harvard commencement speech transcript", "speech"),
        ("Mark Zuckerberg blog post Meta AI strategy", "blog"),
        ("Mark Zuckerberg views on privacy social media regulation", "article"),
        ("Mark Zuckerberg Joe Rogan podcast transcript", "interview"),
        ("Mark Zuckerberg Lex Fridman transcript full conversation", "interview"),
        ("Mark Zuckerberg earnings call transcript strategy", "speech"),
        ("Mark Zuckerberg interview about competing with Apple TikTok", "interview"),
        ("Mark Zuckerberg Acquired podcast transcript Meta history", "interview"),
        ("Zuckerberg Files transcript Marquette University", "interview"),
        # Company culture, rules, innovation, motivation
        ("Mark Zuckerberg Meta company culture move fast innovation", "article"),
        ("Mark Zuckerberg management style leadership how Meta operates", "article"),
        ("Mark Zuckerberg motivation purpose why he builds what drives him", "article"),
        ("Meta tech stack infrastructure engineering Llama PyTorch", "article"),
        ("Mark Zuckerberg on competition Apple Google innovation strategy", "article"),
    ]

    for query, doc_type in queries:
        results = exa_search(query, num_results=3)
        for r in results:
            save_result(speaker, r, "exa_" + doc_type, doc_type)


if __name__ == "__main__":
    if not EXA_API_KEY:
        print("ERROR: EXA_API_KEY not set in .env")
        exit(1)

    print(f"Starting Exa.ai content fetch (max {MAX_SEARCHES} searches)")
    print(f"Budget: ~${MAX_SEARCHES * 0.10:.2f} estimated cost\n")

    fetch_elon_musk()
    fetch_sam_altman()
    fetch_dario_amodei()
    fetch_mark_zuckerberg()

    print(f"\n{'='*50}")
    print(f"DONE! Total Exa searches: {SEARCH_COUNT}")
    print(f"Estimated cost: ~${SEARCH_COUNT * 0.10:.2f}")
    print(f"{'='*50}")
