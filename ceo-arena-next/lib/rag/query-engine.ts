import { Pinecone } from "@pinecone-database/pinecone";
import Groq from "groq-sdk";

import { getEnv } from "@/lib/env";
import { PINECONE_INDEX_NAME, GROQ_MODEL, RELEVANCE_THRESHOLD } from "@/lib/constants";
import { HFInferenceEmbedding } from "./embeddings";
import { getSystemPromptForGeneration } from "./prompts";
import { buildSearchQuery, searchWeb, formatWebResults } from "./web-search";

const GREETING_RE = /^(hi|hello|hey|yo|sup|hallo|servus|moin|guten tag|guten morgen|guten abend|what'?s up)[!.,?]*$/i;
const GREETING_PLUS_RE = /^(hi|hello|hey|hallo|servus|moin).*(how are you|how's it going|wie geht|was geht)/i;

interface RetrievedNode {
  score: number;
  text: string;
}

interface HistoryTurn {
  role: string;
  content: string;
}

export class CEOQueryEngine {
  private pineconeIndex: ReturnType<Pinecone["Index"]>;
  private embedModel: HFInferenceEmbedding;
  private groq: Groq;
  private model: string;

  constructor(model = GROQ_MODEL) {
    const env = getEnv();
    const pc = new Pinecone({ apiKey: env.PINECONE_API_KEY });
    this.pineconeIndex = pc.Index(PINECONE_INDEX_NAME);
    this.embedModel = new HFInferenceEmbedding();
    this.groq = new Groq({ apiKey: env.GROQ_API_KEY });
    this.model = model;
  }

  private async retrieve(speaker: string, question: string, topK = 5): Promise<RetrievedNode[]> {
    const queryEmbedding = await this.embedModel.embedQuery(question);
    const results = await this.pineconeIndex.namespace(speaker).query({
      vector: queryEmbedding,
      topK,
      includeMetadata: true,
    });

    return (results.matches ?? []).map((match) => ({
      score: match.score ?? 0,
      text: (match.metadata?.["text"] as string) ?? "",
    }));
  }

  private async callLlm(systemPrompt: string, userMessage: string): Promise<string> {
    const response = await this.groq.chat.completions.create({
      model: this.model,
      temperature: 0.7,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
    });
    return response.choices[0]?.message?.content ?? "";
  }

  private static isSimplePrompt(question: string): boolean {
    const q = question.trim();
    if (GREETING_RE.test(q) || GREETING_PLUS_RE.test(q)) return true;
    const wordCount = q.match(/\w+/g)?.length ?? 0;
    return wordCount <= 2;
  }

  private static assessRelevance(nodes: RetrievedNode[]): boolean {
    if (nodes.length === 0) return false;
    return (nodes[0]?.score ?? 0) >= RELEVANCE_THRESHOLD;
  }

  private stylePlan(question: string, hasHistory: boolean): [string, number | null, number | null] {
    const q = question.trim();
    const lowered = q.toLowerCase();
    const wordCount = q.match(/\w+/g)?.length ?? 0;

    const greetingRe = /^(hi|hello|hey|yo|sup|hallo|servus|moin|guten tag|guten morgen|guten abend)[!.?]*$/i;
    const greetingPlusRe = /^(hi|hello|hey|hallo|servus|moin).*(how are you|how's it going|wie geht|was geht)/i;
    const detailRe = /\b(detail|details|deep|deeper|detailed|step by step|explain in depth|warum|wieso|ausf[uü]hrlich)\b/i;

    if (greetingPlusRe.test(q)) {
      return [
        "Reply in 2-3 short sentences (max 75 words total): give a specific in-character status update, then ask one natural follow-up question.",
        3, 75,
      ];
    }
    if (greetingRe.test(q)) {
      return ["Reply in 1-2 short sentences (max 28 words), in character.", 2, 28];
    }
    if (wordCount <= 4) {
      return ["Reply with one short sentence (max 24 words), in character.", 1, 24];
    }
    if (hasHistory && wordCount <= 12) {
      return [
        "Treat this as a follow-up. Reference relevant recent chat context. Reply in 2-4 short sentences, max 110 words.",
        4, 110,
      ];
    }
    if (wordCount <= 10 && !detailRe.test(lowered)) {
      return ["Reply in 2-4 short sentences, max 100 words, clear and specific.", 4, 100];
    }
    if (detailRe.test(lowered) || wordCount >= 26) {
      return [
        "Give a detailed and structured answer in 6-11 sentences with concrete points, no filler.",
        11, 380,
      ];
    }
    if (wordCount >= 16) {
      return [
        "Give a clear, medium-depth answer in 4-8 sentences with practical specifics.",
        8, 260,
      ];
    }
    return ["Keep it concise but useful: 3-6 sentences with concrete specifics.", 6, 180];
  }

  private speakerMicrostyle(speaker: string, question: string): string {
    const lowered = question.toLowerCase();
    const wordCount = question.match(/\w+/g)?.length ?? 0;
    const complexQuestion = wordCount >= 18 || /\b(why|how|strategy|tradeoff|architecture|roadmap|risk|vergleich|analyse|plan)\b/.test(lowered);

    if (speaker === "elon_musk") {
      return complexQuestion
        ? "Voice: fast, first-principles, slightly provocative. Use one vivid analogy and one short self-correction at most once (example pattern: 'Wait-no, better framing...')."
        : "Voice: punchy and witty. You may add one brief hesitation phrase at most once (example pattern: 'Uh...').";
    }
    if (speaker === "sam_altman") {
      return "Voice: calm founder energy. Start with the core thesis, then practical implications. Balanced optimism with realistic caveats.";
    }
    if (speaker === "dario_amodei") {
      return "Voice: thoughtful and scientific. Make uncertainty explicit where needed, then give the most robust practical takeaway.";
    }
    if (speaker === "mark_zuckerberg") {
      return complexQuestion
        ? "Voice: methodical and precise. Take a brief beat in the first clause, then give structured, execution-focused guidance with concrete wording."
        : "Voice: direct product-builder mode. Slightly slower start, then crisp and practical answer.";
    }
    return "Voice: stay in character and be specific.";
  }

  private formatHistoryContext(history: HistoryTurn[] | null): string {
    if (!history || history.length === 0) return "";

    const lines: string[] = [];
    for (const turn of history.slice(-8)) {
      const role = turn.role ?? "user";
      const content = (turn.content ?? "").trim();
      if (!content || content.startsWith("Error:")) continue;

      let flattened = content.replace(/\s+/g, " ");
      if (flattened.length > 260) {
        flattened = `${flattened.slice(0, 257)}...`;
      }

      const prefix = role === "user" ? "User" : "Assistant";
      lines.push(`${prefix}: ${flattened}`);
    }

    return lines.join("\n");
  }

  private enforceResponseLimits(
    text: string,
    maxSentences: number | null,
    maxWords: number | null,
  ): string {
    let cleaned = text.trim().replace(/\s+/g, " ");
    if (!cleaned) return cleaned;

    if (maxSentences !== null) {
      const parts = cleaned.split(/(?<=[.!?])\s+/);
      cleaned = parts.slice(0, maxSentences).join(" ").trim();
    }

    if (maxWords !== null) {
      const words = cleaned.split(/\s+/);
      if (words.length > maxWords) {
        cleaned = words.slice(0, maxWords).join(" ").replace(/[,:;]+$/, "");
        if (cleaned && !/[.!?]$/.test(cleaned)) {
          cleaned += ".";
        }
      }
    }

    return cleaned;
  }

  private buildUserMessage(
    question: string,
    hint: string,
    speakerHint: string,
    historyContext: string,
  ): string {
    const parts = [
      `[Response format instruction]\n${hint}`,
      `[Speaker delivery instruction]\n${speakerHint}`,
    ];
    if (historyContext) {
      parts.push(`[Recent conversation context]\n${historyContext}`);
    }
    parts.push(`[Current user message]\n${question}`);
    return parts.join("\n\n");
  }

  async query(
    speaker: string,
    question: string,
    history: HistoryTurn[] | null = null,
  ): Promise<[string, string]> {
    const hasHistory = !!history && history.length > 0;
    const [hint, maxSentences, maxWords] = this.stylePlan(question, hasHistory);
    const speakerHint = this.speakerMicrostyle(speaker, question);
    const historyContext = this.formatHistoryContext(history);

    // FAST PATH — greetings / trivial prompts
    if (CEOQueryEngine.isSimplePrompt(question)) {
      const systemPrompt = getSystemPromptForGeneration(speaker);
      const userMessage = this.buildUserMessage(question, hint, speakerHint, historyContext);
      let text = await this.callLlm(systemPrompt, userMessage);
      text = this.enforceResponseLimits(text, maxSentences, maxWords);
      return [text, "direct"];
    }

    // PHASE 1: Pinecone retrieval
    const nodes = await this.retrieve(speaker, question);

    // PHASE 2: Relevance check + optional web search
    let webContext = "";
    let source = "pinecone";
    if (!CEOQueryEngine.assessRelevance(nodes)) {
      const searchQuery = buildSearchQuery(speaker, question);
      const results = await searchWeb(searchQuery);
      webContext = formatWebResults(results);
      if (webContext) {
        source = "web+pinecone";
      }
    }

    // PHASE 3: Generate with combined context
    const pineconeContext = nodes
      .filter((n) => n.text)
      .map((n) => n.text)
      .join("\n\n");

    const systemPrompt = getSystemPromptForGeneration(speaker, pineconeContext, webContext);
    const userMessage = this.buildUserMessage(question, hint, speakerHint, historyContext);
    let text = await this.callLlm(systemPrompt, userMessage);
    text = this.enforceResponseLimits(text, maxSentences, maxWords);
    return [text, source];
  }

  async debate(
    question: string,
    speakers: string[] | null = null,
  ): Promise<Record<string, string>> {
    const speakerList = speakers ?? ["elon_musk", "sam_altman", "dario_amodei", "mark_zuckerberg"];
    const responses: Record<string, string> = {};

    for (const speaker of speakerList) {
      const [text] = await this.query(speaker, question);
      responses[speaker] = text;
    }

    return responses;
  }
}

// Lazy singleton for serverless
let _engine: CEOQueryEngine | null = null;

export function getEngine(): CEOQueryEngine {
  if (!_engine) {
    _engine = new CEOQueryEngine();
  }
  return _engine;
}
