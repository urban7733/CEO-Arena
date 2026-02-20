import { z } from "zod";

const envSchema = z.object({
  PINECONE_API_KEY: z.string().min(1),
  GROQ_API_KEY: z.string().min(1),
  HF_TOKEN: z.string().optional(),
});

let _env: z.infer<typeof envSchema> | null = null;

export function getEnv() {
  if (_env) return _env;
  _env = envSchema.parse({
    PINECONE_API_KEY: process.env.PINECONE_API_KEY,
    GROQ_API_KEY: process.env.GROQ_API_KEY,
    HF_TOKEN: process.env.HF_TOKEN,
  });
  return _env;
}
