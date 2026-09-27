import { tool } from 'ai';
import { z } from 'zod';
import { evaluate } from 'mathjs';

export const calculatorTool = tool({
  description: 'Safely evaluate mathematical expressions, solve equations, and do unit conversions. Use this for ANY math.',
  parameters: z.object({
    expression: z.string().describe('The math expression, e.g. "sqrt(25) + 10*2" or "12% of 250"'),
  }),
  execute: async ({ expression }) => {
    try {
      const result = evaluate(expression);
      return { expression, result, success: true };
    } catch (error: any) {
      return { expression, error: error.message, success: false };
    }
  },
});
