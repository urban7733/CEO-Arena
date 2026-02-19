from bs4 import BeautifulSoup
import trafilatura

from .base_scraper import BaseScraper


class TranscriptScraper(BaseScraper):
    def scrape_transcript(
        self,
        url: str,
        source: str,
        title: str = "",
        date: str = "",
        interviewer: str = "",
    ) -> dict | None:
        resp = self.fetch(url)
        if not resp:
            return None

        content = trafilatura.extract(resp.text, include_comments=False)
        if not content:
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            content = soup.get_text(separator="\n", strip=True)

        if not content or len(content) < 200:
            print(f"  [SKIP] Too little content from {url}")
            return None

        if not title:
            soup = BeautifulSoup(resp.text, "lxml")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

        metadata = {}
        if interviewer:
            metadata["interviewer"] = interviewer

        doc = self.make_document(
            content=content,
            source=source,
            source_url=url,
            doc_type="interview",
            title=title,
            date=date,
            metadata=metadata,
        )
        self.save_document(doc)
        return doc

    def scrape_lex_fridman(self, episode_url: str, guest_name: str, date: str = "") -> dict | None:
        return self.scrape_transcript(
            url=episode_url,
            source="lex_fridman_podcast",
            title=f"Lex Fridman Podcast - {guest_name}",
            date=date,
            interviewer="Lex Fridman",
        )
