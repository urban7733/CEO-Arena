import { NextResponse } from "next/server";
import { fromError } from "zod-validation-error";

import { chatRequestSchema } from "@/types/api";
import { DISPLAY_NAMES } from "@/lib/constants";
import { getEngine } from "@/lib/rag/query-engine";
import type { SpeakerId } from "@/types";

export const maxDuration = 60;

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON" }, { status: 400 });
  }

  const parsed = chatRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { detail: fromError(parsed.error).toString() },
      { status: 422 },
    );
  }

  const { speaker, message, history } = parsed.data;

  try {
    const engine = getEngine();
    const historyTurns = history?.map((h) => ({ role: h.role, content: h.content })) ?? null;
    const [responseText, source] = await engine.query(speaker, message, historyTurns);

    return NextResponse.json({
      speaker,
      speaker_name: DISPLAY_NAMES[speaker as SpeakerId] ?? speaker,
      message: responseText,
      source,
    });
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : "Internal server error";
    console.error("Chat API error:", errorMessage, err instanceof Error ? err.stack : "");
    return NextResponse.json({ detail: errorMessage }, { status: 500 });
  }
}
