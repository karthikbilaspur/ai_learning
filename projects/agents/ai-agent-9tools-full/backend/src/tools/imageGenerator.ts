import { tool } from 'ai';
import { z } from 'zod';

export const imageGeneratorTool = tool({
  description: 'Generate an image from a text prompt. Use when user asks to create, draw, visualize something.',
  parameters: z.object({
    prompt: z.string().describe('Detailed image prompt'),
    style: z.enum(['realistic', 'anime', '3d', 'minimalist']).default('realistic').optional(),
  }),
  execute: async ({ prompt, style = 'realistic' }) => {
    const key = process.env.OPENAI_API_KEY;
    if (!key) return { warning: 'OPENAI_API_KEY not set', prompt, imageUrl: `https://via.placeholder.com/512?text=${encodeURIComponent(prompt.slice(0,20))} (mock)` };
    // For real use, call OpenAI Images or Replicate
    // const openai = new OpenAI({ apiKey: key });
    // const result = await openai.images.generate({ model: 'dall-e-3', prompt: `${style} style: ${prompt}` });
    // return { prompt, imageUrl: result.data[0].url };
    return { prompt, style, status: 'Image generation called (wire up OpenAI key in production)', imageUrl: null };
  },
});
