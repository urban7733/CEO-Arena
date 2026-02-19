"""
Query engine for CEO Arena.
Uses Groq (Llama 3.3 70B) for generation and HuggingFace for embeddings.
Retrieves relevant context from Pinecone and generates responses in CEO character.
"""
import os
import re
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

    def _style_plan(self, question: str, has_history: bool) -> tuple[str, int | None, int | None]:
        """Return style instruction plus hard output limits."""
        q = question.strip()
        lowered = q.lower()
        word_count = len(re.findall(r"\w+", q))

        greeting_re = re.compile(
            r"^(hi|hello|hey|yo|sup|hallo|servus|moin|guten tag|guten morgen|guten abend)[!.?]*$",
            re.IGNORECASE,
        )
        greeting_plus_re = re.compile(
            r"^(hi|hello|hey|hallo|servus|moin).*(how are you|how's it going|wie geht|was geht)",
            re.IGNORECASE,
        )
        detail_re = re.compile(
            r"\b(detail|details|deep|deeper|detailed|step by step|explain in depth|warum|wieso|ausf[uü]hrlich)\b",
            re.IGNORECASE,
        )

        if greeting_plus_re.search(q):
            return (
                "Reply in 2-3 short sentences (max 75 words total): give a specific in-character status "
                "update, then ask one natural follow-up question.",
                3,
                75,
            )
        if greeting_re.match(q):
            return ("Reply in 1-2 short sentences (max 28 words), in character.", 2, 28)
        if word_count <= 4:
            return ("Reply with one short sentence (max 24 words), in character.", 1, 24)
        if has_history and word_count <= 12:
            return (
                "Treat this as a follow-up. Reference relevant recent chat context. "
                "Reply in 2-4 short sentences, max 110 words.",
                4,
                110,
            )
        if word_count <= 10 and not detail_re.search(lowered):
            return ("Reply in 2-4 short sentences, max 100 words, clear and specific.", 4, 100)
        if detail_re.search(lowered) or word_count >= 26:
            return (
                "Give a detailed and structured answer in 6-11 sentences with concrete points, no filler.",
                11,
                380,
            )
        if word_count >= 16:
            return (
                "Give a clear, medium-depth answer in 4-8 sentences with practical specifics.",
                8,
                260,
            )
        return (
            "Keep it concise but useful: 3-6 sentences with concrete specifics.",
            6,
            180,
        )

    def _speaker_microstyle(self, speaker: str, question: str) -> str:
        """Speaker-specific delivery hint so voices feel distinct."""
        lowered = question.lower()
        word_count = len(re.findall(r"\w+", question))
        complex_question = word_count >= 18 or bool(
            re.search(r"\b(why|how|strategy|tradeoff|architecture|roadmap|risk|vergleich|analyse|plan)\b", lowered)
        )

        if speaker == "elon_musk":
            if complex_question:
                return (
                    "Voice: fast, first-principles, slightly provocative. Use one vivid analogy and one short "
                    "self-correction at most once (example pattern: 'Wait-no, better framing...')."
                )
            return (
                "Voice: punchy and witty. You may add one brief hesitation phrase at most once "
                "(example pattern: 'Uh...')."
            )

        if speaker == "sam_altman":
            return (
                "Voice: calm founder energy. Start with the core thesis, then practical implications. "
                "Balanced optimism with realistic caveats."
            )

        if speaker == "dario_amodei":
            return (
                "Voice: thoughtful and scientific. Make uncertainty explicit where needed, then give the most "
                "robust practical takeaway."
            )

        if speaker == "mark_zuckerberg":
            if complex_question:
                return (
                    "Voice: methodical and precise. Take a brief beat in the first clause, then give structured, "
                    "execution-focused guidance with concrete wording."
                )
            return (
                "Voice: direct product-builder mode. Slightly slower start, then crisp and practical answer."
            )

        return "Voice: stay in character and be specific."

    def _format_history_context(self, history: list[dict] | None) -> str:
        """Build compact recent conversation context for the current query."""
        if not history:
            return ""

        lines: list[str] = []
        for turn in history[-8:]:
            role = turn.get("role", "user")
            content = str(turn.get("content", "")).strip()
            if not content or content.startswith("Error:"):
                continue

            flattened = " ".join(content.split())
            if len(flattened) > 260:
                flattened = f"{flattened[:257]}..."

            prefix = "User" if role == "user" else "Assistant"
            lines.append(f"{prefix}: {flattened}")

        return "\n".join(lines)

    def _enforce_response_limits(
        self,
        text: str,
        max_sentences: int | None,
        max_words: int | None,
    ) -> str:
        """Apply hard sentence/word limits to keep answers concise."""
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return cleaned

        if max_sentences is not None:
            parts = re.split(r"(?<=[.!?])\s+", cleaned)
            cleaned = " ".join(parts[:max_sentences]).strip()

        if max_words is not None:
            words = cleaned.split()
            if len(words) > max_words:
                cleaned = " ".join(words[:max_words]).rstrip(",:;")
                if cleaned and cleaned[-1] not in ".!?":
                    cleaned += "."

        return cleaned

    def query(self, speaker: str, question: str, history: list[dict] | None = None) -> str:
        """Ask a question to a specific CEO."""
        engine = self._get_engine(speaker)
        has_history = bool(history)
        hint, max_sentences, max_words = self._style_plan(question, has_history=has_history)
        speaker_hint = self._speaker_microstyle(speaker, question)
        history_context = self._format_history_context(history)

        if history_context:
            styled_question = (
                f"[Response format instruction]\n{hint}\n\n"
                f"[Speaker delivery instruction]\n{speaker_hint}\n\n"
                f"[Recent conversation context]\n{history_context}\n\n"
                f"[Current user message]\n{question}"
            )
        else:
            styled_question = (
                f"[Response format instruction]\n{hint}\n\n"
                f"[Speaker delivery instruction]\n{speaker_hint}\n\n"
                f"[Current user message]\n{question}"
            )

        response = engine.query(styled_question)
        text = str(response)
        return self._enforce_response_limits(text, max_sentences=max_sentences, max_words=max_words)

    def debate(self, question: str, speakers: list[str] | None = None) -> dict[str, str]:
        """Ask the same question to multiple CEOs for a debate/comparison."""
        if speakers is None:
            speakers = ["elon_musk", "sam_altman", "dario_amodei", "mark_zuckerberg"]

        responses = {}
        for speaker in speakers:
            print(f"  Asking {speaker}...")
            responses[speaker] = self.query(speaker, question)

        return responses
