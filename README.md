# Grindemy Backend Scaffold

FastAPI backend for the Grindemy project, focused on scraping, analytics, visualization APIs, and database endpoints for a Lovable frontend.

## Features

- Google News RSS ingestion for business, technology, politics, and sustainability.
- Topic clustering with TF-IDF + K-Means to auto-generate hashtags.
- Keyword co-occurrence network with NetworkX centrality metrics.
- Visualization-ready APIs for K-Means scatter and network graph.
- Research-paper retrieval via Crossref API.
- Daily "Sustainable Finance Corner" concept endpoint.
- Discussion board APIs (auto-seed from generated topics + manual threads/messages).
- SQLModel schema compatible with SQLite (default) and PostgreSQL (`DATABASE_URL`).
- CORS support via `ALLOWED_ORIGINS` for Lovable Cloud.

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
- `POST /news/clusters?k=4`
- `GET /news/clusters`
- `GET /news/clusters/visualization?k=4`
- `POST /news/network?top_n=25`
- `GET /news/network`
- `GET /news/network/visualization?top_n=25`
- `GET /research/papers?topic=green%20bond`
- `GET /research/concept`
- `POST /discussions/seed`
- `GET /discussions/threads`
- `POST /discussions/threads`
- `GET /discussions/threads/{thread_id}/messages`
- `POST /discussions/threads/{thread_id}/messages`

## Visualization payload formats

### K-Means visualization (`GET /news/clusters/visualization`)
Returns:
- `points[]` with:
  - `article_id`
  - `title`
  - `category`
  - `cluster_id`
  - `cluster_hashtag`
  - `x`, `y` (2D coordinates after PCA reduction)

### Network visualization (`GET /news/network/visualization`)
Returns:
- `nodes[]` with `id`, `label`, `degree_centrality`, `betweenness_centrality`
- `edges[]` with `source`, `target`, `weight`

## GitHub integration checklist

1. Push this branch to your GitHub repository.
2. In GitHub repo **Settings → Secrets and variables → Actions**, add any deployment secrets you need.
3. Confirm the included workflow runs (`.github/workflows/backend-ci.yml`) on push/PR.
4. Deploy this FastAPI service to your preferred host (Render/Railway/Fly/EC2).
5. Set `ALLOWED_ORIGINS` to your Lovable domain (for example `https://your-app.lovable.app`).
6. Use the deployed base URL in your Lovable project for API calls.

## Lovable prompt (copy/paste)

Use this prompt in Lovable to wire your charts directly to backend APIs:

```text
Build two data visualizations on my Grindemy page and fetch data from my backend.

Backend base URL: {{BACKEND_URL}}

1) K-Means Topic Map
- Call GET {{BACKEND_URL}}/news/clusters/visualization?k=4
- Render a scatter plot where:
  - x-axis = x
  - y-axis = y
  - color = cluster_hashtag
  - tooltip = title + category + cluster_hashtag
- Add a refresh button that calls POST {{BACKEND_URL}}/news/clusters?k=4 first, then reloads the visualization endpoint.

2) News Keyword Network Graph
- Call GET {{BACKEND_URL}}/news/network/visualization?top_n=25
- Render a force-directed graph where:
  - nodes = nodes
  - edges = edges
  - node size = degree_centrality
  - tooltip = label + degree_centrality + betweenness_centrality
  - edge thickness = weight
- Add a refresh button that calls POST {{BACKEND_URL}}/news/network?top_n=25 first, then reloads the visualization endpoint.

General requirements:
- Include loading, empty-state, and error-state UI.
- Use my theme: white background, green accents, dark blue text.
- Add note: "AI-generated summaries and clustering may contain inaccuracies."
```

## Notes

- This scaffold keeps AI summarization logic outside core APIs so you can plug in your preferred LLM provider later.
- For production, replace wildcard CORS with explicit frontend origins.
