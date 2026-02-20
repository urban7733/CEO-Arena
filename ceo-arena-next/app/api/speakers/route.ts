import { NextResponse } from "next/server";
import { SPEAKERS } from "@/lib/constants";

export async function GET() {
  return NextResponse.json(
    SPEAKERS.map((s) => ({
      id: s.id,
      name: s.name,
      company: s.company,
    })),
  );
}
