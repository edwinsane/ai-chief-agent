# AI Chief Agent

A modular multi-agent system built with **LangChain** and **LangGraph**.
A central **SupervisorAgent** orchestrates specialized subagents through a directed pipeline.

## Architecture

```
main.py                  Entry point — runs the pipeline from the CLI
run_dashboard.sh         One-command dashboard launcher
deploy/
└── ai-chief-dashboard.service   systemd unit for VPS auto-start
.streamlit/
└── config.toml          Streamlit server settings (0.0.0.0:8501)
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
│   └── app.py           Streamlit monitoring UI (auto-refresh, status cards)
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

## Dashboard

The Streamlit dashboard provides real-time monitoring: agent status, last-run timestamp, and full run history. It auto-refreshes every 30 seconds.

```bash
# Local
./run_dashboard.sh
# Then open http://localhost:8501
```

## VPS Deployment (Ubuntu/Debian)

### 1. Upload the project

```bash
scp -r . deploy@your-vps:/opt/ai-chief-agent
```

### 2. Set up the environment on the VPS

```bash
ssh deploy@your-vps
cd /opt/ai-chief-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install the systemd service (recommended)

```bash
sudo cp deploy/ai-chief-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-chief-dashboard   # start on boot
sudo systemctl start ai-chief-dashboard    # start now
sudo systemctl status ai-chief-dashboard   # verify
```

The service auto-restarts on crash (5 s delay). View logs with:

```bash
sudo journalctl -u ai-chief-dashboard -f
```

### 4. Open the firewall

```bash
sudo ufw allow 8501/tcp
```

Then visit `http://your-vps-ip:8501`.

### Alternative: screen session

If you prefer not to use systemd:

```bash
screen -S dashboard
cd /opt/ai-chief-agent
./run_dashboard.sh
# Press Ctrl+A then D to detach
```

Re-attach later:

```bash
screen -r dashboard
```

## Requirements

- Python 3.11+
- See `requirements.txt` for Python packages
