const HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2";
const HF_API_URL = `https://router.huggingface.co/hf-inference/pipeline/feature-extraction/${HF_MODEL}`;

export class HFInferenceEmbedding {
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const hfToken = process.env.HF_TOKEN;
    if (hfToken) {
      headers["Authorization"] = `Bearer ${hfToken}`;
    }
    return headers;
  }

  async embed(texts: string[]): Promise<number[][]> {
    const response = await fetch(HF_API_URL, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ inputs: texts, options: { wait_for_model: true } }),
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      throw new Error(`HF Inference API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<number[][]>;
  }

  async embedQuery(query: string): Promise<number[]> {
    const result = await this.embed([query]);
    const first = result[0];
    if (!first) throw new Error("Empty embedding result");
    return first;
  }
}
