import { tool } from 'ai';
import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

const UPLOAD_DIR = path.resolve(process.cwd(), 'uploads');

export const fileReaderTool = tool({
  description: 'Read contents of user-uploaded files (txt, md, json, csv). Use to analyze documents.',
  parameters: z.object({
    filename: z.string().describe('Filename in uploads folder, e.g. "report.txt"'),
    maxChars: z.number().default(8000).optional(),
  }),
  execute: async ({ filename, maxChars = 8000 }) => {
    try {
      const filePath = path.join(UPLOAD_DIR, filename);
      // Security: prevent path traversal
      if (!filePath.startsWith(UPLOAD_DIR)) throw new Error('Invalid path');
      const content = await fs.readFile(filePath, 'utf-8');
      return { filename, content: content.slice(0, maxChars), truncated: content.length > maxChars, totalLength: content.length };
    } catch (e: any) {
      return { filename, error: e.message };
    }
  },
});
