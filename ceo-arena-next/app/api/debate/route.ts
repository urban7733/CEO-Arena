import { NextResponse } from "next/server";
import { fromError } from "zod-validation-error";

import { debateRequestSchema } from "@/types/api";
import { DISPLAY_NAMES, SPEAKER_IDS } from "@/lib/constants";
import { getEngine } from "@/lib/rag/query-engine";
import type { SpeakerId } from "@/types";

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON" }, { status: 400 });
  }

  const parsed = debateRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { detail: fromError(parsed.error).toString() },
      { status: 422 },
    );
  }

  const { message, speakers } = parsed.data;
  const speakerList = speakers ?? SPEAKER_IDS;

  try {
    const engine = getEngine();
    const responses = await engine.debate(message, speakerList);

    return NextResponse.json(
      Object.entries(responses).map(([speaker, msg]) => ({
        speaker,
        speaker_name: DISPLAY_NAMES[speaker as SpeakerId] ?? speaker,
        message: msg,
      })),
    );
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json({ detail: errorMessage }, { status: 500 });
  }
}
