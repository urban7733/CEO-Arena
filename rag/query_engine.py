"""
Query engine for CEO Arena.
Uses Groq (Llama 3.3 70B) for generation and FastEmbed (ONNX) for embeddings.
Three response paths:
  1. Fast path   — greetings/trivial → LLM with persona + biography only
  2. RAG path    — good Pinecone hits (score ≥ 0.35) → Pinecone context + LLM
  3. Agentic path — weak Pinecone hits → Pinecone + DuckDuckGo web search + LLM
"""
import logging
import os
import re

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from .prompts import get_system_prompt_for_generation
from .web_search import build_search_query, format_web_results, search_web

load_dotenv()

logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "ceo-arena"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"

RELEVANCE_THRESHOLD = 0.35

_GREETING_RE = re.compile(
    r"^(hi|hello|hey|yo|sup|hallo|servus|moin|guten tag|guten morgen|guten abend|what'?s up)[!.,?]*$",
    re.IGNORECASE,
)
_GREETING_PLUS_RE = re.compile(
    r"^(hi|hello|hey|hallo|servus|moin).*(how are you|how's it going|wie geht|was geht)",
    re.IGNORECASE,
)


class CEOQueryEngine:
    """Query engine that lets you ask questions to any of the 4 CEOs."""

    def __init__(self, model: str = GROQ_MODEL):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.pinecone_index = self.pc.Index(PINECONE_INDEX_NAME)

        self.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
        self.llm = Groq(model=model, temperature=0.7, api_key=os.getenv("GROQ_API_KEY"))

        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

        # Cache retrievers per speaker
        self._retrievers: dict = {}

    # ------------------------------------------------------------------
    # Retriever (replaces old _get_engine)
    # ------------------------------------------------------------------
    def _get_retriever(self, speaker: str):
        """Get or create a retriever for a specific CEO namespace."""
        if speaker in self._retrievers:
            return self._retrievers[speaker]

        vector_store = PineconeVectorStore(
            pinecone_index=self.pinecone_index,
            namespace=speaker,
        )
        index = VectorStoreIndex.from_vector_store(vector_store)
        retriever = index.as_retriever(similarity_top_k=5)

        self._retrievers[speaker] = retriever
        return retriever

    # ------------------------------------------------------------------
    # Classification helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_simple_prompt(question: str) -> bool:
        """Check if question is a simple greeting or trivial (≤2 words)."""
        q = question.strip()
        if _GREETING_RE.match(q) or _GREETING_PLUS_RE.search(q):
            return True
        word_count = len(re.findall(r"\w+", q))
        return word_count <= 2

    @staticmethod
    def _assess_relevance(nodes: list[NodeWithScore]) -> bool:
        """Return True if the top Pinecone result is relevant enough."""
        if not nodes:
            return False
        top_score = nodes[0].score
        if top_score is None:
            return True  # can't assess, assume relevant
        return top_score >= RELEVANCE_THRESHOLD

    # ------------------------------------------------------------------
    # LLM generation
    # ------------------------------------------------------------------
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Direct LLM call via Groq with a system prompt + user message."""
        from llama_index.core.llms import ChatMessage, MessageRole

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ChatMessage(role=MessageRole.USER, content=user_message),
        ]
        response = self.llm.chat(messages)
        return str(response.message.content)

    def _direct_llm_call(
        self,
        speaker: str,
        question: str,
        hint: str,
        speaker_hint: str,
        history_context: str,
    ) -> str:
        """Fast path: LLM with persona + biography only, no retrieval."""
        system_prompt = get_system_prompt_for_generation(speaker)
        user_message = self._build_user_message(question, hint, speaker_hint, history_context)
        return self._call_llm(system_prompt, user_message)

    def _generate_response(
        self,
        speaker: str,
        question: str,
        pinecone_context: str,
        web_context: str,
        hint: str,
        speaker_hint: str,
        history_context: str,
    ) -> str:
        """Full generation with all context (Pinecone + optional web)."""
        system_prompt = get_system_prompt_for_generation(
            speaker,
            pinecone_context=pinecone_context,
            web_context=web_context,
        )
        user_message = self._build_user_message(question, hint, speaker_hint, history_context)
        return self._call_llm(system_prompt, user_message)

    @staticmethod
    def _build_user_message(
        question: str,
        hint: str,
        speaker_hint: str,
        history_context: str,
    ) -> str:
        """Assemble the user message with style hints and history."""
        parts = [
            f"[Response format instruction]\n{hint}",
            f"[Speaker delivery instruction]\n{speaker_hint}",
        ]
        if history_context:
            parts.append(f"[Recent conversation context]\n{history_context}")
        parts.append(f"[Current user message]\n{question}")
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Style / micro-style helpers (unchanged from original)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Main query — 3-path flow
    # ------------------------------------------------------------------
    def query(self, speaker: str, question: str, history: list[dict] | None = None) -> tuple[str, str]:
        """Ask a question to a specific CEO.

        Returns (response_text, source) where source is one of:
        "direct", "pinecone", "web+pinecone".
        """
        has_history = bool(history)
        hint, max_sentences, max_words = self._style_plan(question, has_history=has_history)
        speaker_hint = self._speaker_microstyle(speaker, question)
        history_context = self._format_history_context(history)

        # FAST PATH — greetings / trivial prompts
        if self._is_simple_prompt(question):
            logger.info("Fast path for %s: %r", speaker, question)
            text = self._direct_llm_call(speaker, question, hint, speaker_hint, history_context)
            text = self._enforce_response_limits(text, max_sentences, max_words)
            return text, "direct"

        # PHASE 1: Pinecone retrieval
        retriever = self._get_retriever(speaker)
        nodes = retriever.retrieve(question)

        # PHASE 2: Relevance check + optional web search
        web_context = ""
        source = "pinecone"
        if not self._assess_relevance(nodes):
            logger.info("Weak Pinecone hits for %s, triggering web search", speaker)
            search_query = build_search_query(speaker, question)
            results = search_web(search_query, speaker)
            web_context = format_web_results(results)
            if web_context:
                source = "web+pinecone"

        # PHASE 3: Generate with combined context
        pinecone_context = "\n\n".join(n.text for n in nodes if n.text)
        text = self._generate_response(
            speaker, question, pinecone_context, web_context,
            hint, speaker_hint, history_context,
        )
        text = self._enforce_response_limits(text, max_sentences, max_words)
        return text, source

    def debate(self, question: str, speakers: list[str] | None = None) -> dict[str, str]:
        """Ask the same question to multiple CEOs for a debate/comparison."""
        if speakers is None:
            speakers = ["elon_musk", "sam_altman", "dario_amodei", "mark_zuckerberg"]

        responses = {}
        for speaker in speakers:
            print(f"  Asking {speaker}...")
            text, _source = self.query(speaker, question)
            responses[speaker] = text

        return responses
