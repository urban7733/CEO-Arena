import { z } from "zod";

const speakerIdSchema = z.enum([
  "elon_musk",
  "sam_altman",
  "dario_amodei",
  "mark_zuckerberg",
]);

const chatHistoryTurnSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string().min(1).max(1200),
});

export const chatRequestSchema = z.object({
  speaker: speakerIdSchema,
  message: z.string().min(1).max(2000),
  history: z.array(chatHistoryTurnSchema).optional(),
});

export const debateRequestSchema = z.object({
  message: z.string().min(1).max(2000),
  speakers: z.array(speakerIdSchema).optional(),
});

export const chatResponseSchema = z.object({
  speaker: z.string(),
  speaker_name: z.string(),
  message: z.string(),
  source: z.string().optional(),
});

export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type DebateRequest = z.infer<typeof debateRequestSchema>;
export type ChatResponseData = z.infer<typeof chatResponseSchema>;
export type ChatHistoryTurn = z.infer<typeof chatHistoryTurnSchema>;
