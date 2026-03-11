# Grindemy Backend Scaffold

FastAPI backend for the Grindemy project, focused on scraping, analytics, and database APIs for a Lovable frontend.

## Features

- Google News RSS ingestion for business, technology, politics, and sustainability.
- Topic clustering with TF-IDF + K-Means to auto-generate hashtags.
- Keyword co-occurrence network with NetworkX centrality metrics.
- Research-paper retrieval via Crossref API.
- Daily "Sustainable Finance Corner" concept endpoint.
- Discussion board APIs (auto-seed from generated topics + manual threads/messages).
- SQLModel schema compatible with SQLite (default) and PostgreSQL (`DATABASE_URL`).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## API overview

- `GET /health`
- `POST /news/ingest`
- `GET /news/articles`
- `POST /news/clusters`
- `GET /news/clusters`
- `POST /news/network`
- `GET /news/network`
- `GET /research/papers?topic=green%20bond`
- `GET /research/concept`
- `POST /discussions/seed`
- `GET /discussions/threads`
- `POST /discussions/threads`
- `GET /discussions/threads/{thread_id}/messages`
- `POST /discussions/threads/{thread_id}/messages`

## Notes

- This scaffold intentionally keeps AI summarization logic outside of core APIs so you can plug in your own LLM provider later.
- Add CORS middleware once you connect your Lovable frontend domain.
