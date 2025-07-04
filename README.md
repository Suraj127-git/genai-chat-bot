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

## Project Structure

```
├── AINews/               # News storage directory
│   ├── daily_summary.md
│   ├── weekly_summary.md
│   └── monthly_summary.md
├── src/
│   └── langgraphagenticai/
│       ├── LLMS/         # LLM provider implementations
│       ├── common/       # Shared utilities and configurations
│       ├── graph/        # LangChain graph definitions
│       ├── nodes/        # Graph nodes and components
│       ├── state/        # State management
│       ├── tools/        # Custom tool implementations
│       └── ui/           # User interface components
├── .env.example          # Environment variable template
└── requirements.txt      # Python dependencies
```

## Setup

1. **Environment Setup**:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # OR
   .venv\Scripts\activate    # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Usage

1. **Start the Application**:
   ```bash
   python -m streamlit run app.py
   ```

2. **Access the Interface**:
   - Open your browser and navigate to `http://localhost:8501`
   - The chat interface will be available for interaction

3. **News Summaries**:
   - Daily summaries are generated automatically
   - Access summaries in the `AINews` directory
   - View through the chat interface using specific commands

## Development

- **Adding New LLM Providers**:
  1. Create a new provider class in `src/langgraphagenticai/LLMS/`
  2. Implement the required interface methods
  3. Register the provider in the configuration

- **Custom Tools**:
  1. Add new tool implementations in `src/langgraphagenticai/tools/`
  2. Register tools with the agent system

- **Logging**:
  - Logs are stored in the `logs` directory
  - Configure log levels in `src/langgraphagenticai/common/logger.py`
  - Better Stack integration available through environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.