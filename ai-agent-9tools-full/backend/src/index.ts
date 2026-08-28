import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { runAgent } from './agents/orchestrator';

dotenv.config();
const app = express();
app.use(cors({ origin: '*' }));
app.use(express.json());

app.get('/', (req, res) => res.json({ status: 'AI Agent with 9 tools running', tools: Object.keys(require('./tools').allTools || ['calculator','web_search','code_executor','file_reader','weather','calendar','database_query','image_generator','memory']) }));
app.get('/health', (req, res) => res.json({ ok: true }));

app.post('/api/chat', async (req, res) => {
  try {
    const { messages } = req.body;
    if (!messages) return res.status(400).json({ error: 'messages required' });
    const result = await runAgent(messages);
    result.pipeDataStreamToResponse(res);
  } catch (e: any) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`✅ Agent running on http://localhost:${PORT}`));
