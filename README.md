# Standard RAG

> **WARNING: Intentionally Insecure Demo**
>
> This is a deliberately vulnerable RAG application for testing security scanners.
> **Do NOT deploy publicly.** Run locally only.

## Why This Exists

This repo serves as a **test target** for the [LLM Production Safety Scanner](https://github.com/musabdulai-io/llm-production-safety-scanner). It demonstrates common failure modes in RAG applications:

- No input validation or prompt injection protection
- No output filtering or guardrails
- No access controls on retrieved documents
- No rate limiting or cost controls

Use this to generate sample security reports and understand what vulnerabilities look like in practice.

## Features

- Document upload (PDF, TXT, Markdown)
- Semantic search with vector embeddings
- AI-powered question answering
- Session-based document management

## Tech Stack

- **Framework**: FastAPI + LangChain
- **Vector DB**: Pinecone (Serverless)
- **Database**: PostgreSQL
- **LLM**: OpenAI (GPT-4o-mini)
- **Document Parser**: pypdf
- **Frontend**: Next.js + Material-UI

## Local Setup

### Prerequisites

- Docker and Docker Compose
- Pinecone API Key
- OpenAI API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/musabdulai-io/standard-rag.git
cd standard-rag
```

2. Copy environment template:
```bash
cp .env.example .env
```

3. Add your API keys to `.env`:
```bash
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
```

4. Start the services:
```bash
docker compose up
```

5. Access locally:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Seed Sample Data (Optional)

Sample documents are auto-seeded on first startup. To manually seed:

```bash
docker compose exec backend python -m scripts.seed
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (Next.js + MUI)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│                       (FastAPI)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│   PostgreSQL    │ │ Pinecone  │ │    Storage      │
│   (Documents)   │ │ (Vectors) │ │  (Local/GCS)    │
└─────────────────┘ └───────────┘ └─────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rag/documents` | Upload a document (PDF, TXT, MD) |
| GET | `/api/v1/rag/documents` | List all documents |
| DELETE | `/api/v1/rag/documents/{id}` | Delete a document |
| POST | `/api/v1/rag/search` | Search documents |
| POST | `/api/v1/rag/query` | Ask a question |
| GET | `/health` | Health check |

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_INDEX` | Pinecone index name | standard-rag |
| `PINECONE_CLOUD` | Pinecone cloud provider | aws |
| `PINECONE_REGION` | Pinecone region | us-east-1 |
| `DATABASE_URL` | PostgreSQL connection string | See .env.example |

## License

MIT

---

## Contact

- **Website**: [musabdulai.com](https://musabdulai.com)
- **Book a call**: [Schedule a meeting](https://calendly.com/musabdulai/guardrails-sprint)
