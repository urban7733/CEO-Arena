"""
Ingest processed JSON data into Pinecone vector store.
Creates separate namespaces per CEO for targeted retrieval.
"""
import json
from pathlib import Path

from llama_index.core import Document, Settings, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from config import PROCESSED_DIR, SPEAKERS

import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "ceo-arena"
# HuggingFace embedding model (free, runs locally)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 outputs 384 dimensions
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def load_documents(speaker: str) -> list[Document]:
    """Load processed JSON for a speaker into LlamaIndex Documents."""
    filepath = PROCESSED_DIR / f"{speaker}.json"
    if not filepath.exists():
        print(f"  [SKIP] No data for {speaker}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        # Create document with rich metadata for filtering
        doc = Document(
            text=item["content"],
            metadata={
                "speaker": item["speaker"],
                "source": item["source"],
                "source_url": item.get("source_url", ""),
                "date": item.get("date", ""),
                "type": item["type"],
                "title": item.get("title", ""),
                "doc_id": item["id"],
            },
            excluded_llm_metadata_keys=["doc_id", "source_url"],
            excluded_embed_metadata_keys=["doc_id", "source_url"],
        )
        docs.append(doc)

    print(f"  [LOADED] {speaker}: {len(docs)} documents")
    return docs


def create_pinecone_index():
    """Create Pinecone index if it doesn't exist."""
    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,  # all-MiniLM-L6-v2 = 384 dims
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"  [CREATED] Index '{PINECONE_INDEX_NAME}'")
    else:
        print(f"  [EXISTS] Index '{PINECONE_INDEX_NAME}'")

    return pc.Index(PINECONE_INDEX_NAME)


def ingest_speaker(speaker: str, pinecone_index):
    """Ingest a single speaker's data into their Pinecone namespace."""
    print(f"\nIngesting {speaker}...")

    docs = load_documents(speaker)
    if not docs:
        return

    # Configure embedding model (HuggingFace, runs locally - free!)
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.embed_model = embed_model

    # Chunk documents
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    # Create vector store with speaker-specific namespace
    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index,
        namespace=speaker,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Build index (this embeds and upserts to Pinecone)
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )

    print(f"  [DONE] {speaker}: ingested into namespace '{speaker}'")
    return index


def ingest_all():
    """Ingest all speakers into Pinecone."""
    print("=" * 50)
    print("CEO ARENA - Data Ingestion Pipeline")
    print("=" * 50)

    pinecone_index = create_pinecone_index()

    for speaker in SPEAKERS:
        ingest_speaker(speaker, pinecone_index)

    print(f"\n{'='*50}")
    print("INGESTION COMPLETE!")
    print(f"Index: {PINECONE_INDEX_NAME}")
    print(f"Namespaces: {', '.join(SPEAKERS.keys())}")
    print(f"{'='*50}")


if __name__ == "__main__":
    ingest_all()
