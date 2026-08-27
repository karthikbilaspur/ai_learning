import { z } from 'zod';

const envSchema = z.object({
  OPENAI_API_KEY: z.string().min(1, "Missing OPENAI_API_KEY"),
  OPENAI_MODEL: z.string().default("gpt-4o-mini"),
});

export const env = envSchema.parse(process.env);