"""
Normalize all raw JSON documents into a single processed JSON file per speaker.
Deduplicates by content hash and validates schema.
"""
import json
import hashlib
from pathlib import Path
from config import RAW_DIR, PROCESSED_DIR, SPEAKERS


def content_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def validate_document(doc: dict) -> bool:
    required = ["id", "speaker", "source", "content", "type"]
    for key in required:
        if key not in doc or not doc[key]:
            return False
    if len(doc["content"]) < 50:
        return False
    return True


def normalize_speaker(speaker: str) -> list[dict]:
    raw_dir = RAW_DIR / speaker
    if not raw_dir.exists():
        print(f"  [SKIP] No raw data for {speaker}")
        return []

    docs = []
    seen_hashes = set()

    for json_file in sorted(raw_dir.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                doc = json.load(f)

            if not validate_document(doc):
                print(f"  [SKIP] Invalid document: {json_file.name}")
                continue

            # Deduplicate by content
            h = content_hash(doc["content"])
            if h in seen_hashes:
                print(f"  [SKIP] Duplicate: {json_file.name}")
                continue
            seen_hashes.add(h)

            # Ensure consistent schema
            normalized = {
                "id": doc["id"],
                "speaker": speaker,
                "source": doc.get("source", "unknown"),
                "source_url": doc.get("source_url", ""),
                "date": doc.get("date", ""),
                "type": doc["type"],
                "title": doc.get("title", ""),
                "content": doc["content"].strip(),
                "metadata": doc.get("metadata", {}),
            }
            docs.append(normalized)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [ERROR] Failed to process {json_file.name}: {e}")

    return docs


def normalize_all():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for speaker in SPEAKERS:
        print(f"\nNormalizing {speaker}...")
        docs = normalize_speaker(speaker)

        output_file = PROCESSED_DIR / f"{speaker}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)

        print(f"  [SAVED] {output_file.name}: {len(docs)} documents")
        total += len(docs)

    print(f"\n=== TOTAL: {total} documents normalized ===")


if __name__ == "__main__":
    normalize_all()
