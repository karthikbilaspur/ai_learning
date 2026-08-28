import { tool } from 'ai';
import { z } from 'zod';

export const codeExecutorTool = tool({
  description: 'Execute JavaScript or Python code safely in a sandbox. Use for coding tasks, data analysis, algorithms.',
  parameters: z.object({
    language: z.enum(['javascript', 'python']).default('javascript'),
    code: z.string().describe('The code to execute'),
  }),
  execute: async ({ language, code }) => {
    // Using Piston API for safe sandboxing - no eval()!
    try {
      const res = await fetch('https://emkc.org/api/v2/piston/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, version: '*', files: [{ content: code }] }),
      });
      const data = await res.json();
      return { language, code, output: data.run?.output, stdout: data.run?.stdout, stderr: data.run?.stderr };
    } catch (e: any) {
      return { error: e.message, language, code };
    }
  },
});
