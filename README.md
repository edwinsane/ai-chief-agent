# AI Chief Agent

A modular multi-agent system built with **LangChain** and **LangGraph**.
A central **SupervisorAgent** orchestrates specialized subagents through a directed pipeline.

## Architecture

```
main.py                  Entry point — runs the pipeline from the CLI
app/
├── agents/
│   ├── base.py          Abstract base class shared by all agents
│   ├── supervisor.py    Orchestrator — builds a LangGraph StateGraph
│   ├── research_agent.py   Gathers raw information on a topic
│   ├── trend_agent.py      Extracts trends from research data
│   └── qa_agent.py         Validates outputs before delivery
├── core/
│   ├── config.py        Central settings (env vars + defaults)
│   └── logger.py        Shared logger
├── integrations/        (future) External API connectors
├── dashboard/
│   └── app.py           Streamlit monitoring UI
└── storage/
    └── database.py      SQLite persistence layer
tests/                   Unit & integration tests
```

### Pipeline flow

```
[SupervisorAgent]
        │
        ▼
  ResearchAgent  →  TrendAgent  →  QAAgent  →  Result
```

## Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI key (required for LLM calls; stubs work without it)
cp .env.example .env             # then edit .env
# or
export OPENAI_API_KEY="sk-..."

# 4. Run the pipeline
python main.py                   # default topic
python main.py "quantum computing"  # custom topic

# 5. Launch the dashboard
streamlit run app/dashboard/app.py
```

## Configuration

All settings live in `app/core/config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `LLM_TEMPERATURE` | `0` | Sampling temperature |
| `DATABASE_URL` | `sqlite:///data/agents.db` | SQLite database path |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Debug mode |

## Requirements

- Python 3.11+
- See `requirements.txt` for Python packages
