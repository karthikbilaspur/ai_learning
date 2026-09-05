# Production RAG Agent

A production-oriented Retrieval-Augmented Generation (RAG) agent built with FastAPI, hybrid retrieval, cross-encoder reranking, persistent indexing, deterministic citation validation, tool execution, evaluation, tracing, cost tracking, and Docker support.

This project started as a compact RAG/agent prototype and has been upgraded to address two critical reliability gaps:

Citation correctness is evaluated rather than hardcoded.
The retrieval index is persisted and reused across application restarts.
Features
RAG pipeline
text
User Query
   │
   ▼
FastAPI
   │
   ▼
Agent Orchestrator
   │
   ├── Hybrid Retrieval
   │      ├── BM25
   │      └── Dense Embeddings / TF-IDF fallback
   │
   ├── Cross-Encoder Reranking
   │
   ├── Calculator Tool (when appropriate)
   │
   └── LLM Generation
          │
          ▼
   Citation Validation
          │
          ├── Valid → return answer
          │
          └── Invalid/unsupported → grounded extractive fallback
Key capabilities
Hybrid BM25 + dense retrieval
FAISS-backed dense search when sentence-transformers and FAISS are available
TF-IDF fallback for lightweight/offline environments
Cross-encoder reranking
Persistent retrieval index with compatibility fingerprinting
Automatic index rebuild when source chunks change
Optional forced index rebuild
Citation extraction and validation
Detection of invalid citations
Claim-to-source overlap validation
No automatic/fabricated citation injection
Grounded fallback answers when generated answers cannot be validated
Calculator tool with AST-based allow-list validation
OpenAI LLM provider
Deterministic mock provider for local development and tests
Request IDs
Rate limiting
Health/readiness endpoints
Tracing and latency metrics
Token and cost accounting
Evaluation and regression-gate support
Docker and Docker Compose support
Streamlit dashboard
Automated tests
Project Structure
text
rag_code-v2/
├── api/
│   ├── main.py
│   ├── middleware.py
│   └── schemas.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── docs.json
│   └── index/                 # generated persistent retrieval index
│
├── evals/
│   ├── answer_metrics.py
│   ├── eval_questions.json
│   ├── latest_metrics.json
│   ├── regression_gate.py
│   ├── retrieval_metrics.py
│   └── run_eval.py
│
├── ingestion/
│   ├── chunker.py
│   ├── index.py
│   └── loader.py
│
├── src/
│   ├── agent.py
│   ├── citation_validator.py
│   ├── config.py
│   ├── cost.py
│   ├── llm.py
│   ├── logging.py
│   ├── prompts.py
│   ├── reranker.py
│   ├── retriever.py
│   ├── tools.py
│   └── tracer.py
│
├── tests/
│   ├── test_agent.py
│   ├── test_retrieval.py
│   └── test_tools.py
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
Requirements
Recommended:

Python 3.11+
pip
Git
Docker + Docker Compose (optional)
The project uses:

FastAPI
Pydantic v2
Sentence Transformers
FAISS
rank-bm25
scikit-learn
OpenAI SDK
Streamlit
pytest
Quick Start
Create a virtual environment
bash
python -m venv .venv
Linux/macOS:

bash
source .venv/bin/activate
Windows:

powershell
.venv\Scripts\activate
Install dependencies
bash
pip install -r requirements.txt
Configure environment

Copy the example environment file:

bash
cp .env.example .env
For Windows:

powershell
copy .env.example .env
For local development, the default configuration uses the mock LLM:

env
LLM_PROVIDER=mock
To use OpenAI:

env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
Never commit real API keys to source control.

Run the API
From the project root:

bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
The API will be available at:

text
<http://localhost:8000>
FastAPI documentation:

text
<http://localhost:8000/docs>

API Endpoints
Health
http
GET /health
Example:

bash
curl <http://localhost:8000/health>
Readiness
http
GET /ready
This reports whether the agent has successfully loaded its document corpus and initialized the retrieval system.

Query
http
POST /query
Example:

bash
curl -X POST <http://localhost:8000/query> \
  -H "Content-Type: application/json" \
  -d '{"question":"What does the knowledge base say about RAG?"}'
A successful response contains:

json
{
  "answer": "...",
  "citations": [
    {
      "doc_id": "doc-1",
      "chunk_id": "chunk-0",
      "text": "...",
      "score": 0.91
    }
  ],
  "trace_id": "...",
  "latency_ms": 123,
  "tokens": {
    "prompt_tokens": 500,
    "completion_tokens": 100,
    "total_tokens": 600
  },
  "cost_usd": 0.0001,
  "retrieval_scores": [0.91, 0.84],
  "tool_calls": []
}
Metrics
http
GET /metrics
Returns dashboard/trace metrics collected by the application.

Persistent Index
Persistent indexing is a core part of this version.

Previously, the application rebuilt the retrieval index every time an AgentOrchestrator was created. The upgraded retriever stores its artifacts under:

text
data/index/
Typical artifacts include:

text
data/index/
├── manifest.json
├── chunks.json
├── embeddings.npy
├── faiss.index
└── tfidf.pkl
Not every file is present simultaneously. The exact artifacts depend on whether dense retrieval or the TF-IDF fallback is active.

How persistence works
At startup:

Documents are loaded.
Documents are chunked.
A fingerprint is calculated from the chunk IDs, document IDs, and chunk text.
The existing index manifest is checked.
If the fingerprint and configuration are compatible, the index is loaded.
If no compatible index exists, the index is rebuilt and saved.
This prevents unnecessary embedding/index construction across application restarts.

Force a rebuild
Set:

env
FORCE_REBUILD_INDEX=true
or rebuild explicitly:

bash
python -m ingestion.index
After a successful rebuild, the persistent index is written to the configured index directory.

Citation Correctness
Citation correctness is intentionally treated as a reliability feature rather than a formatting feature.

The system expects citations in the form:

text
[doc_id:chunk_id]
For example:

text
The system uses hybrid retrieval [doc-1:chunk-0].
Validation pipeline
Generated answers are checked for:

Whether citations exist.
Whether each citation refers to a retrieved chunk.
Whether factual claims can be associated with citations.
Whether cited source text contains sufficient meaningful-token overlap with the claim.
The validator returns structured information such as:

json
{
  "valid": true,
  "citation_count": 2,
  "valid_citation_count": 2,
  "invalid_citations": [],
  "claims": [
    {
      "claim": "...",
      "supported": true,
      "overlap": 0.42,
      "citation": ["doc-1", "chunk-0"]
    }
  ],
  "score": 1.0
}
Important safety behavior
The system does not do this:

text
No citation in answer
        ↓
Append first retrieved chunk citation
That behavior can create plausible-looking but incorrect citations.

Instead:

text
Generated answer
        ↓
Citation validation
        ↓
Unsupported?
        │
        ├── No → return generated answer
        │
        └── Yes → generate grounded extractive fallback
The fallback uses sentences directly from retrieved evidence and attaches the citation belonging to that evidence.

This makes citation failure visible instead of silently manufacturing provenance.

Current limitation: citation validation is deterministic and primarily lexical. Token overlap is useful for detecting many failures but does not constitute full semantic entailment. A future production upgrade should add an NLI model or an independent LLM judge.

Retrieval
The retriever combines lexical and semantic signals.

BM25
BM25 handles:

exact terms
rare words
identifiers
keyword-heavy questions
Dense retrieval
When available, the default embedding model is:

text
sentence-transformers/all-MiniLM-L6-v2
FAISS performs vector similarity search.

TF-IDF fallback
If Sentence Transformers or FAISS cannot be loaded, the retriever falls back to:

text
scikit-learn TF-IDF
This makes local development and tests possible without requiring the dense stack.

Hybrid scoring
The retriever combines dense and lexical scores using:

text
hybrid = alpha *dense + (1 - alpha)* bm25
The default:

env
HYBRID_ALPHA=0.6
means dense retrieval contributes 60% and BM25 contributes 40%.

Reranking
Initial retrieval intentionally fetches more candidates than the final answer requires.

For example:

text
20 retrieved candidates
        ↓
cross-encoder reranker
        ↓
top 5 final chunks
The default reranker is:

text
cross-encoder/ms-marco-MiniLM-L-6-v2
Reranking can be disabled:

env
RERANKER_ENABLED=false
This is useful for lightweight deployments or environments where the model is unavailable.

Ingestion
The default data source is:

text
data/docs.json
Documents are loaded and split into overlapping chunks.

Default configuration:

env
CHUNK_SIZE=300
CHUNK_OVERLAP=50
Build/rebuild the index:

bash
python -m ingestion.index
The indexer uses the same persistent retrieval mechanism as the API.

Agent and Tools
The AgentOrchestrator coordinates:

retrieval
reranking
calculator execution
LLM generation
citation validation
fallback generation
tracing
Calculator
The calculator is intentionally restricted.

It does not use:

python
eval(...)
or:

python
exec(...)
Expressions are parsed through Python's AST and evaluated only when the operation/function is explicitly allowed.

This prevents arbitrary Python execution through calculator input.

Example:

text
What is 25 * 4 + 10?
can be routed to the calculator.

LLM Configuration
Default local mode:

env
LLM_PROVIDER=mock
OpenAI mode:

env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
Additional controls include:

env
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_TEMPERATURE=0.1
The mock provider is useful for:

tests
CI
offline development
deterministic demonstrations
Evaluation
Evaluation questions are stored in:

text
evals/eval_questions.json
Run evaluation:

bash
python -m evals.run_eval
Results are written to:

text
evals/latest_metrics.json
The evaluation suite includes metrics for:

Recall@5
MRR
Faithfulness
Answer Relevancy
Citation Correctness
Average Cost
p95 Latency
Citation correctness is dynamic
Citation correctness is calculated from actual generated answers and retrieved evidence.

It is not a hardcoded 1.0.

This means a citation regression can now cause the regression gate to fail.

Regression Gate
The default regression thresholds are defined in:

text
evals/regression_gate.py
Current baseline:

text
Recall@5             0.90
MRR                  0.80
Faithfulness         0.90
Answer Relevancy     0.85
Citation Correctness 0.95
The gate applies a tolerance before reporting regressions.

You can integrate the gate into CI by running evaluation first and then passing the resulting metrics to the gate.

Testing
Run all tests:

bash
pytest -q
The test suite covers:

agent execution
retrieval behavior
persistent index reuse
calculator validation
calculator security
citation validation
grounded fallback behavior
For development, run:

bash
pytest -q
before committing changes.

Docker
Build and run with Docker Compose:

bash
docker compose up --build
Services:

API: <http://localhost:8000>
API docs:<http://localhost:8000/docs>
Dashboard: <http://localhost:8501>
The Docker setup mounts:

text
./data  → /app/data
./evals → /app/evals
so persistent indexes and evaluation output survive container recreation.

Dashboard
The Streamlit dashboard provides visibility into:

evaluation metrics
costs
traces
latency
retrieval information
Start manually:

bash
streamlit run dashboard/app.py
or use Docker Compose.

Configuration Reference
Important environment variables:

Variable Default Purpose
LLM_PROVIDER mock mock or openai
OPENAI_API_KEY empty OpenAI API key
OPENAI_MODEL gpt-4o-mini LLM model
LOG_LEVEL INFO Application logging level
DATA_PATH data/docs.json Source document file
INDEX_DIR data/index Persistent index directory
FORCE_REBUILD_INDEX false Force index regeneration
EMBEDDING_MODEL sentence-transformers/all-MiniLM-L6-v2 Dense embedding model

RERANKER_MODEL cross-encoder/ms-marco-MiniLM-L-6-v2 Reranker
TOP_K 5 Final context size
RETRIEVAL_CANDIDATES 20 Initial retrieval size
HYBRID_ALPHA 0.6 Dense/BM25 weighting
RERANKER_ENABLED true Enable cross-encoder
CHUNK_SIZE 300 Chunk size
CHUNK_OVERLAP 50 Chunk overlap
LLM_TIMEOUT_SECONDS 30 LLM timeout
LLM_MAX_RETRIES 2 LLM retry count
LLM_TEMPERATURE 0.1 Generation temperature
MONTHLY_BUDGET_USD 50 Cost budget
RATE_LIMIT_REQUESTS 60 Requests per rate-limit window
RATE_LIMIT_WINDOW_SECONDS 60 Rate-limit window
MAX_QUESTION_LENGTH 2000 Maximum query length

Production Considerations
This project is significantly more robust than a basic RAG demo, but several areas should still be upgraded before a high-scale production deployment.

Recommended next steps
Persistent distributed state
The current tracing and rate-limiting implementation is process-local.

For multiple API workers/replicas, use:

Redis for distributed rate limiting/caching
PostgreSQL or another durable store for application metadata
OpenTelemetry for distributed tracing
Production vector storage
FAISS persistence is useful for a single service, but larger deployments may benefit from:

Qdrant
pgvector
Milvus
Weaviate
Choose based on scale, filtering requirements, operational constraints, and infrastructure.

Semantic citation evaluation
The current citation validator is deterministic.

For stronger evaluation, add:

NLI/entailment scoring
LLM-as-judge
claim extraction
source-to-claim entailment
citation precision/recall
A useful production metric is:

text
Citation Precision = supported cited claims / all cited claims
and:

text
Citation Recall = supported claims with citations / all factual claims
Authentication and authorization
The sample API does not implement a full identity/access-control layer.

Production deployments should add:

authentication
API keys or OAuth2/OIDC
tenant isolation
authorization
request quotas
Document lifecycle
A larger ingestion system should support:

incremental indexing
document versioning
deletes
metadata filters
scheduled ingestion
ingestion status
failed-document retry
index version management
Design Principles
This project follows several important principles.

Never manufacture provenance: If the model does not produce a verifiable citation, do not invent one.
Retrieval is evidence, not truth: A retrieved chunk is candidate evidence. The application should still validate whether the generated claim is supported.
Fail closed on grounding: When a generated answer cannot be validated, prefer a grounded fallback or an explicit lack-of-evidence response over an attractive hallucination.
Separate retrieval from generation: Retrieval, reranking, tools, validation, and generation are independently testable components.
Make failures observable: The system exposes trace IDs, retrieval scores, token counts, costs, tool calls, citation validation, and latency. This makes debugging significantly easier.
Development Workflow
Recommended workflow:

bash
 Install

pip install -r requirements.txt

 Configure
cp .env.example .env

Build index
python -m ingestion.index

Run tests
pytest -q

Run evaluation
python -m evals.run_eval

Start API
uvicorn api.main:app --reload
For a clean rebuild:

bash
FORCE_REBUILD_INDEX=true python -m ingestion.index
Troubleshooting
The index rebuilds unexpectedly
Check:

text
data/index/manifest.json
The manifest contains the source fingerprint and retrieval configuration.

If the source documents or chunking configuration changed, a rebuild is expected.

You can also force a clean rebuild:

bash
rm -rf data/index
python -m ingestion.index
Dense retrieval is unavailable
The system automatically falls back to TF-IDF when Sentence Transformers or FAISS cannot be loaded.

Check the installed dependencies:

bash
pip install -r requirements.txt
OpenAI calls fail
Verify:

env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
and confirm that the selected model is available to the configured account.

For local testing, use:

env
LLM_PROVIDER=mock
Citation validation fails
This is intentionally treated as a reliability failure.

Inspect:

citation_validation
retrieved citations
generated claims
overlap scores
If the generated answer cannot be grounded, the orchestrator should return its grounded fallback rather than fabricate a citation.

License
Add your preferred project license here before public distribution.

Roadmap
Potential future upgrades:

 NLI-based citation entailment
 LLM-as-judge evaluation
 OpenTelemetry integration
 Redis distributed rate limiting
 Persistent trace storage
 pgvector/Qdrant backend
 Incremental document indexing
 Metadata filtering
 Query rewriting
 Multi-query retrieval
 Context compression
 Hybrid reranking strategies
 Authentication and authorization
 Multi-tenant isolation
 Streaming responses
 Background ingestion workers
 CI/CD regression gate
 Model/provider failover
