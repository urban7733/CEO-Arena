"""
Exa.ai Scraper - Semantic search for CEO content.
Uses Exa's API to find interviews, articles, and transcripts.

Setup: Add EXA_API_KEY to your .env file
Get key from: https://exa.ai
"""
import os
import requests
from .base_scraper import BaseScraper


class ExaScraper(BaseScraper):
    API_URL = "https://api.exa.ai/search"

    def __init__(self, speaker: str):
        super().__init__(speaker)
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            print("[WARN] EXA_API_KEY not set in .env - Exa scraper disabled")

    def search(self, query: str, num_results: int = 10, content: bool = True) -> list[dict]:
        if not self.api_key:
            return []

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "numResults": num_results,
            "contents": {
                "text": True
            } if content else {},
            "type": "neural",
        }

        try:
            resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            docs = []
            for result in data.get("results", []):
                text = result.get("text", "")
                if not text or len(text) < 100:
                    continue

                doc = self.make_document(
                    content=text,
                    source="exa_search",
                    source_url=result.get("url", ""),
                    doc_type="article",
                    title=result.get("title", ""),
                    date=result.get("publishedDate", "")[:10] if result.get("publishedDate") else "",
                    metadata={"exa_score": result.get("score", 0)},
                )
                docs.append(doc)

            self.save_documents(docs)
            return docs

        except requests.RequestException as e:
            print(f"  [ERROR] Exa API error: {e}")
            return []

    def find_interviews(self, person_name: str, num_results: int = 10) -> list[dict]:
        return self.search(f"{person_name} interview transcript full text", num_results)

    def find_speeches(self, person_name: str, num_results: int = 10) -> list[dict]:
        return self.search(f"{person_name} speech keynote transcript", num_results)

    def find_opinions(self, person_name: str, topic: str, num_results: int = 5) -> list[dict]:
        return self.search(f"{person_name} opinion on {topic} in his own words", num_results)
