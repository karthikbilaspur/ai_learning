import { encodingForModel } from 'js-tiktoken';

export function countTokens(text: string) {
  try {
    const enc = encodingForModel("gpt-4o-mini");
    const n = enc.encode(text).length;
    return n;
  } catch {
    return Math.ceil(text.length / 4);
  }
}