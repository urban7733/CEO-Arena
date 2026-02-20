import type { Speaker, SpeakerId } from "@/types";

export const SPEAKER_IDS: SpeakerId[] = [
  "elon_musk",
  "sam_altman",
  "dario_amodei",
  "mark_zuckerberg",
];

export const SPEAKERS: Speaker[] = [
  { id: "elon_musk", name: "Elon Musk", company: "Tesla, SpaceX, xAI", avatar: "/avatars/elon_musk.png" },
  { id: "sam_altman", name: "Sam Altman", company: "OpenAI", avatar: "/avatars/sam_altman.png" },
  { id: "dario_amodei", name: "Dario Amodei", company: "Anthropic", avatar: "/avatars/dario_amodei.png" },
  { id: "mark_zuckerberg", name: "Mark Zuckerberg", company: "Meta", avatar: "/avatars/mark_zuckerberg.png" },
];

export const DISPLAY_NAMES: Record<SpeakerId, string> = {
  elon_musk: "Elon Musk",
  sam_altman: "Sam Altman",
  dario_amodei: "Dario Amodei",
  mark_zuckerberg: "Mark Zuckerberg",
};

export const PINECONE_INDEX_NAME = "ceo-arena";
export const GROQ_MODEL = "llama-3.3-70b-versatile";
export const RELEVANCE_THRESHOLD = 0.35;
