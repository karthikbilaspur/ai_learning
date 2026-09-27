import { encoding_for_model } from "js-tiktoken";

type ModelPricing = {
  input: number;
  output: number;
};

const PRICING: Record<
  string,
  ModelPricing
> = {
  "gpt-4o-mini": {
    input: 0.00015,
    output: 0.0006,
  },

  "gpt-4o": {
    input: 0.0025,
    output: 0.01,
  },
};

const FALLBACK_MODEL =
  "gpt-4o-mini";

export function countTokens(
  text: string,
  model = FALLBACK_MODEL,
): number {
  if (!text) {
    return 0;
  }

  try {
    const encoding =
      encoding_for_model(
        model as Parameters<
          typeof encoding_for_model
        >[0],
      );

    const count =
      encoding.encode(text).length;

    encoding.free();

    return count;
  } catch {
    return Math.ceil(text.length / 4);
  }
}

export function calculateCost(
  model: string,
  inputTokens: number,
  outputTokens: number,
) {
  const price =
    PRICING[model] ??
    PRICING[FALLBACK_MODEL];

  const input =
    (inputTokens / 1000) *
    price.input;

  const output =
    (outputTokens / 1000) *
    price.output;

  return {
    input,
    output,
    total: input + output,
  };
}