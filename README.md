# Standard RAG

A standard RAG (Retrieval-Augmented Generation) system built with industry-standard tools.

**Demo**: [rag.musabdulai.com](https://rag.musabdulai.com)

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
- **Document Parser**: Unstructured
- **Frontend**: Next.js + Material-UI

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- Pinecone API Key
- OpenAI API Key

### Setup

1. Clone and navigate to the project:
```bash
cd standard-rag
```

2. Run the setup script:
```bash
./setup.sh
```

3. Update your environment:
```bash
# Edit .env and add your API keys
nano .env
```

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Your Pinecone API key

4. Start the services:
```bash
docker compose up
```

5. Access the application:
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

- **Email**: [hello@musabdulai.com](mailto:hello@musabdulai.com)
- **Book a call**: [Schedule a meeting](https://calendly.com/musabdulai/ai-security-check)
- **Website**: [musabdulai.com](https://musabdulai.com)
