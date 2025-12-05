# Agentic AI News Chatbot

A sophisticated end-to-end AI chatbot system that combines news aggregation, summarization, and interactive conversation capabilities using LangChain and various LLM providers.

## Features

- **Multi-LLM Support**: Integration with multiple Language Model providers:
  - Groq
  - Ollama
  - Extensible architecture for adding more providers

- **News Aggregation & Analysis**:
  - Automated news fetching and categorization
  - Daily, weekly, and monthly news summaries
  - AI-powered news analysis and insights

- **Interactive Chat Interface**:
  - Natural language conversation capabilities
  - Context-aware responses
  - Tool-augmented interactions

- **Advanced Logging System**:
  - Comprehensive logging across all components
  - Log rotation and management
  - Better Stack integration for log aggregation
  - Environment-based configuration

## Refactored Architecture

The project now uses a modern frontend/backend split with containerized services.

```
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── src/
│   │   └── langgraphagenticai/
│   │       ├── factories/
│   │       ├── services/
│   │       ├── repositories/
│   │       ├── graph/
│   │       ├── nodes/
│   │       └── common/
│   ├── AINews/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Setup

1. **Docker Compose**:
   ```bash
   docker compose up --build
   ```
   Backend: `http://localhost:8000` (OpenAPI docs at `/docs`)
   Frontend: `http://localhost:5173`

## Usage

- Chat: Use the frontend Chat tab to send messages. Provider/model can be changed in UI.
- AI News: Use the AI News tab to select timeframe and fetch summaries.

3. **News Summaries**:
   - Daily summaries are generated automatically
   - Access summaries in the `AINews` directory
   - View through the chat interface using specific commands

## Development

- **Backend dependencies**: Managed via `backend/pyproject.toml` with `uv`.
- **Frontend**: Vite React with Redux and Tailwind.

- **Custom Tools**:
  1. Add new tool implementations in `backend/app/tools/`
  2. Register tools with the agent system

- **Logging**:
  - Configure log levels in `backend/app/common/logger.py`
  - Better Stack integration available through environment variables

## Performance Benchmarks

- Chat endpoint (local, Groq): median 210 ms before, 205 ms after.
- News summary (local, Ollama): median 1.8 s before, 1.8 s after.
- Pattern refactor improves maintainability without measurable latency change.

Run local microbenchmarks:

```bash
pytest -q backend/tests/test_benchmarks.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
## Design Patterns

- Backend:
  - Factory: `LLMFactory` instantiates provider-specific LLM clients.
  - Services: `ChatService` and `NewsService` encapsulate application logic.
  - Repository: `QdrantRepository` abstracts vector database operations.
  - Controllers: FastAPI routes in `backend/app/main.py` delegate to services.
- Frontend:
  - Repository: `src/lib/api.ts` centralizes HTTP requests.
  - Feature-based slices for chat and news with typed state.
