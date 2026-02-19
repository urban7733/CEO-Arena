from pathlib import Path
from PyPDF2 import PdfReader
import io

from .base_scraper import BaseScraper


class PDFScraper(BaseScraper):
    def download_and_extract(
        self,
        url: str,
        source: str,
        title: str = "",
        date: str = "",
    ) -> dict | None:
        resp = self.fetch(url)
        if not resp:
            return None

        try:
            reader = PdfReader(io.BytesIO(resp.content))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            content = "\n\n".join(text_parts)

            if not content or len(content) < 100:
                print(f"  [SKIP] Too little text extracted from PDF: {url}")
                return None

            doc = self.make_document(
                content=content,
                source=source,
                source_url=url,
                doc_type="pdf",
                title=title or url.split("/")[-1],
                date=date,
                metadata={"pages": len(reader.pages)},
            )
            self.save_document(doc)
            return doc

        except Exception as e:
            print(f"  [ERROR] Failed to parse PDF from {url}: {e}")
            return None

    def extract_local_pdf(
        self,
        filepath: str | Path,
        source: str,
        title: str = "",
        date: str = "",
    ) -> dict | None:
        try:
            reader = PdfReader(filepath)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            content = "\n\n".join(text_parts)
            if not content or len(content) < 100:
                print(f"  [SKIP] Too little text in PDF: {filepath}")
                return None

            doc = self.make_document(
                content=content,
                source=source,
                source_url=f"file://{filepath}",
                doc_type="pdf",
                title=title or Path(filepath).stem,
                date=date,
                metadata={"pages": len(reader.pages)},
            )
            self.save_document(doc)
            return doc

        except Exception as e:
            print(f"  [ERROR] Failed to parse local PDF {filepath}: {e}")
            return None
