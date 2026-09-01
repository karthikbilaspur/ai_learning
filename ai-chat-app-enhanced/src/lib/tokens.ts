import { encoding_for_model } from "js-tiktoken";

const PRICING: Record<string, { input: number; output: number }> = {
  "gpt-4o-mini": { input: 0.00015, output: 0.0006 },
  "gpt-4o": { input: 0.0025, output: 0.01 },
};

export function countTokens(text: string) {
  if (!text) return 0;
  try {
    const enc = encoding_for_model("gpt-4o-mini" as never);
    const count = enc.encode(text).length;
    enc.free();
    return count;
  } catch {
    return Math.ceil(text.length / 4);
  }
}

export function calculateCost(model: string, inputTokens: number, outputTokens: number) {
  const price = PRICING[model] ?? PRICING["gpt-4o-mini"];
  const input = (inputTokens / 1000) * price.input;
  const output = (outputTokens / 1000) * price.output;
  return { input, output, total: input + output };
}
