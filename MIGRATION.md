# Migration Guide

## Overview

The application has been refactored from a single Streamlit-based Python app to a frontend/backend architecture using React + Redux and FastAPI.

## What Changed

- UI: Streamlit UI replaced by React (Vite) with Tailwind and Redux.
- API: FastAPI provides REST endpoints with OpenAPI documentation.
- Orchestration: Existing LangGraph nodes and logic are reused through backend endpoints.
- Vector DB: Qdrant runs as a service via docker-compose.
 - Patterns: Introduced Factory, Services, and Repository layers.

## Mapping Old to New

- Streamlit chat input → Frontend Chat tab → `api.chat()` → POST `/chat`.
- AI News fetch button → Frontend AI News tab → `api.newsSummary()` → POST `/news/summary`.
- Qdrant sidebar → Health checks via `/health` and Docker service status.

## Data and Files

- Data and Files

- News summaries continue to be stored under `backend/AINews/`.
- Python modules are located under `backend/app/` and imported by the backend.
- LLM creation moved to `factories/llm_factory.py`.
- Endpoint logic moved to `services/chat_service.py` and `services/news_service.py`.

## Environment Variables

- `GROQ_API_KEY` for Groq provider.
- `QDRANT_URL` automatically set to `http://qdrant:6333` in docker-compose.
- Optional Logtail vars: `LOGTAIL_SOURCE_TOKEN`, `LOGTAIL_HOST`.

## Local Development

- `docker compose up --build` to run all services.
- Frontend dev mode: `npm run dev` in `frontend/` if running backend locally.
- Backend dev mode: `uv pip install -r` from `backend/pyproject.toml` then `uvicorn backend.app.main:app --reload`.

## Compatibility Notes

- Logger now falls back to console if Logtail env vars are missing.
- Groq model requires `GROQ_API_KEY`. Use Ollama for local testing by setting `DEFAULT_PROVIDER=Ollama` and `DEFAULT_MODEL=llama3.2:1b`.
