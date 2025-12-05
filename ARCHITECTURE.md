# Architecture Overview

## Frontend

- React functional components with hooks.
- Redux Toolkit for state management.
- Tailwind CSS for styling and responsive UI.
- Vite for development and build.

## Backend

- FastAPI application exposing REST endpoints.
- LangChain and LangGraph used to build and run graphs.
- Qdrant integration via repository wrapping `QdrantManager`.
- OpenAPI docs available at `/docs`.

## Services

- Dockerized `backend`, `frontend`, and `qdrant` services.
- `docker-compose.yml` sets networking, volumes, and health checks.

## Data Flow

- Frontend calls backend endpoints.
- Backend builds graphs via `EnhancedGraphBuilder` and nodes.
- Results returned as JSON to the frontend.
- AI News summaries saved under `backend/AINews/`.

## Diagram

```
Frontend (Vite/React/Redux)
  ├─ features/
  │   ├─ chat (slice, components)
  │   └─ news (slice, components)
  └─ lib/api.ts  ← Repository for HTTP calls

Backend (FastAPI)
  ├─ app/
  │   ├─ main.py  ← Controllers (routes)
  │   ├─ factories/llm_factory.py  ← Factory
  │   ├─ services/ (chat_service.py, news_service.py) ← Application services
  │   ├─ repositories/qdrant_repository.py ← Repository
  │   ├─ graph/                ← Orchestration
  │   ├─ nodes/                ← Strategies/Steps
  │   ├─ database/qdrant_manager.py ← DB adapter
  │   ├─ state/                ← Graph state types
  │   └─ common/logger.py      ← Logging
```

## Logging and Error Handling

- Central logger config with safe fallback to console.
- Backend endpoints return HTTP errors on failures.

## Testing and CI

- Pytest-based backend tests.
- GitHub Actions CI runs backend tests and builds frontend.
