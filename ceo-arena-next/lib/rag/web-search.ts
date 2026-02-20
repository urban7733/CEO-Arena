const PERSONALITY_PREFIXES: Record<string, string> = {
  elon_musk: "engineering physics first-principles",
  sam_altman: "AI startups exponential-growth",
  dario_amodei: "AI-safety research empirical",
  mark_zuckerberg: "platform open-source product-strategy",
};

export function buildSearchQuery(speaker: string, question: string): string {
  const prefix = PERSONALITY_PREFIXES[speaker] ?? "";
  return `${prefix} ${question}`.trim();
}

interface SearchResult {
  title: string;
  href: string;
  body: string;
}

export async function searchWeb(
  query: string,
  maxResults = 5,
): Promise<SearchResult[]> {
  try {
    const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
    const response = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; CEOArena/1.0)",
      },
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) return [];

    const html = await response.text();
    const results: SearchResult[] = [];

    const resultRegex = /<a[^>]+class="result__a"[^>]+href="([^"]*)"[^>]*>([\s\S]*?)<\/a>[\s\S]*?<a[^>]+class="result__snippet"[^>]*>([\s\S]*?)<\/a>/g;
    let match: RegExpExecArray | null;
    while ((match = resultRegex.exec(html)) !== null && results.length < maxResults) {
      const href = decodeURIComponent((match[1] ?? "").replace(/.*uddg=/, "").replace(/&.*/, ""));
      const title = (match[2] ?? "").replace(/<[^>]*>/g, "").trim();
      const body = (match[3] ?? "").replace(/<[^>]*>/g, "").trim();
      if (title && body) {
        results.push({ title, href, body });
      }
    }

    return results;
  } catch {
    return [];
  }
}

export function formatWebResults(results: SearchResult[], maxWords = 500): string {
  if (results.length === 0) return "";

  const lines: string[] = [];
  let wordCount = 0;

  for (const r of results) {
    const entry = `- ${r.title}: ${r.body} (source: ${r.href})`;
    const entryWords = entry.split(/\s+/).length;
    if (wordCount + entryWords > maxWords) break;
    lines.push(entry);
    wordCount += entryWords;
  }

  return lines.join("\n");
}
