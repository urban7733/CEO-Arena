"""
Lightweight embedding class using HuggingFace Inference API.
No PyTorch, no sentence-transformers — just HTTP calls.
Uses the same all-MiniLM-L6-v2 model as our Pinecone index.
"""
import os
import requests

HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_URL = f"https://router.huggingface.co/hf-inference/pipeline/feature-extraction/{HF_MODEL}"


class HFInferenceEmbedding:
    """Lightweight embedding using HuggingFace Inference API (free tier with token)."""

    def __init__(self):
        self.model_name = HF_MODEL

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        return headers

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Call HuggingFace Inference API for embeddings."""
        response = requests.post(
            HF_API_URL,
            headers=self._get_headers(),
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        return self.embed([query])[0]
