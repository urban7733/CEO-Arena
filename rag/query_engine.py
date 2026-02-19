"""
Query engine for CEO Arena.
Uses Groq (Llama 3.3 70B) for generation and HuggingFace for embeddings.
Retrieves relevant context from Pinecone and generates responses in CEO character.
"""
import os
from dotenv import load_dotenv

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from .prompts import get_system_prompt

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "ceo-arena"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"


class CEOQueryEngine:
    """Query engine that lets you ask questions to any of the 4 CEOs."""

    def __init__(self, model: str = GROQ_MODEL):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.pinecone_index = self.pc.Index(PINECONE_INDEX_NAME)

        # HuggingFace embeddings (free, local)
        self.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

        # Groq LLM (free tier, Llama 3.3 70B)
        self.llm = Groq(model=model, temperature=0.7, api_key=os.getenv("GROQ_API_KEY"))

        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

        # Cache query engines per speaker
        self._engines = {}

    def _get_engine(self, speaker: str):
        """Get or create a query engine for a specific CEO."""
        if speaker in self._engines:
            return self._engines[speaker]

        # Connect to speaker's namespace
        vector_store = PineconeVectorStore(
            pinecone_index=self.pinecone_index,
            namespace=speaker,
        )
        index = VectorStoreIndex.from_vector_store(vector_store)

        # Build query engine with personality prompt
        system_prompt = get_system_prompt(speaker)
        qa_template = PromptTemplate(system_prompt)

        engine = index.as_query_engine(
            similarity_top_k=5,
            text_qa_template=qa_template,
        )

        self._engines[speaker] = engine
        return engine

    def query(self, speaker: str, question: str) -> str:
        """Ask a question to a specific CEO."""
        engine = self._get_engine(speaker)
        response = engine.query(question)
        return str(response)

    def debate(self, question: str, speakers: list[str] | None = None) -> dict[str, str]:
        """Ask the same question to multiple CEOs for a debate/comparison."""
        if speakers is None:
            speakers = ["elon_musk", "sam_altman", "dario_amodei", "mark_zuckerberg"]

        responses = {}
        for speaker in speakers:
            print(f"  Asking {speaker}...")
            responses[speaker] = self.query(speaker, question)

        return responses
