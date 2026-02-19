"""
DuckDuckGo web search wrapper with personality-filtered queries.
Falls back gracefully if search fails.
"""
import logging

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Personality-biased search prefixes
_PERSONALITY_PREFIXES: dict[str, str] = {
    "elon_musk": "engineering physics first-principles",
    "sam_altman": "AI startups exponential-growth",
    "dario_amodei": "AI-safety research empirical",
    "mark_zuckerberg": "platform open-source product-strategy",
}


def build_search_query(speaker: str, question: str) -> str:
    """Prepend personality perspective terms to bias search results."""
    prefix = _PERSONALITY_PREFIXES.get(speaker, "")
    return f"{prefix} {question}".strip()


def search_web(query: str, speaker: str, max_results: int = 5) -> list[dict]:
    """Run a DuckDuckGo search. Returns list of {title, href, body} dicts.

    Wrapped in try/except so failures degrade gracefully to Pinecone-only.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as exc:
        logger.warning("Web search failed for query %r: %s", query, exc)
        return []


def format_web_results(results: list[dict], max_words: int = 500) -> str:
    """Format search results into prompt-ready text, capped at ~max_words."""
    if not results:
        return ""

    lines: list[str] = []
    word_count = 0
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        entry = f"- {title}: {body} (source: {href})"
        entry_words = len(entry.split())
        if word_count + entry_words > max_words:
            break
        lines.append(entry)
        word_count += entry_words

    return "\n".join(lines)
