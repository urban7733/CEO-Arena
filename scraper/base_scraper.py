import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests

from config import RAW_DIR, REQUEST_DELAY, REQUEST_TIMEOUT, USER_AGENT


class BaseScraper:
    def __init__(self, speaker: str):
        self.speaker = speaker
        self.output_dir = RAW_DIR / speaker
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def fetch(self, url: str) -> requests.Response | None:
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            print(f"  [ERROR] Failed to fetch {url}: {e}")
            return None

    def make_document(
        self,
        content: str,
        source: str,
        source_url: str,
        doc_type: str,
        title: str = "",
        date: str = "",
        metadata: dict | None = None,
    ) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "speaker": self.speaker,
            "source": source,
            "source_url": source_url,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "type": doc_type,
            "title": title,
            "content": content.strip(),
            "metadata": metadata or {},
        }

    def save_document(self, doc: dict):
        filename = f"{doc['type']}_{doc['id'][:8]}.json"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        print(f"  [SAVED] {filepath.name} ({len(doc['content'])} chars)")

    def save_documents(self, docs: list[dict]):
        for doc in docs:
            if doc["content"]:
                self.save_document(doc)
        print(f"  [TOTAL] Saved {len(docs)} documents for {self.speaker}")
