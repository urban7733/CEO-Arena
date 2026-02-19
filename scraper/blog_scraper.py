from bs4 import BeautifulSoup
import trafilatura

from .base_scraper import BaseScraper


class BlogScraper(BaseScraper):
    def scrape_blog_post(self, url: str, source: str, title: str = "", date: str = "") -> dict | None:
        resp = self.fetch(url)
        if not resp:
            return None

        # Use trafilatura for clean text extraction
        content = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
        if not content:
            # Fallback to BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            content = soup.get_text(separator="\n", strip=True)

        if not content or len(content) < 100:
            print(f"  [SKIP] Too little content from {url}")
            return None

        if not title:
            soup = BeautifulSoup(resp.text, "lxml")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

        doc = self.make_document(
            content=content,
            source=source,
            source_url=url,
            doc_type="blog",
            title=title,
            date=date,
        )
        self.save_document(doc)
        return doc

    def scrape_blog_index(self, index_url: str, source: str, link_selector: str = "a") -> list[dict]:
        """Scrape all linked posts from a blog index page."""
        resp = self.fetch(index_url)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select(link_selector)

        docs = []
        for link in links:
            href = link.get("href")
            if not href or href.startswith("#") or href.startswith("mailto:"):
                continue
            if not href.startswith("http"):
                # Make absolute URL
                from urllib.parse import urljoin
                href = urljoin(index_url, href)

            title = link.get_text(strip=True)
            doc = self.scrape_blog_post(href, source=source, title=title)
            if doc:
                docs.append(doc)

        return docs
