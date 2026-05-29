# Claude in Production: The Complete AI Agent Playbook

> From first API call to deployed multi-agent system — every pattern, every pitfall, real code.

Most developers can get a Claude demo working in an afternoon. Getting that demo into production — reliable outputs, cost controls, safe multi-agent coordination, real users — is a different problem. This repo is the companion code for the playbook that covers that second step.

**84 pages. 15 chapters. 5 parts. Everything you need to ship Claude-powered software that actually works.**

[![Get the book — $28](https://img.shields.io/badge/Seliq%20AI-Get%20the%20book%20%E2%80%94%20%2428-0A1628?style=for-the-badge&labelColor=0A1628&color=2563EB)](https://seliq-ai.com/seliqopedia/claude-in-production)

---

## Run your first example in 2 minutes

```bash
git clone https://github.com/MernaHesham/claude-in-production-playbook.git
cd claude-in-production-playbook
pip install -r requirements.txt
cp .env.example .env          # add your Anthropic API key
python ch01_foundations/1_hello_claude.py
```

You should see a streaming Claude response in your terminal. From there, work through chapters in order as you read the book — or jump straight to the pattern you need.

---

## What's in this repo

| Part | Chapter | Folder | Topic |
|------|---------|--------|-------|
| I — Foundations | 1 | [ch01_foundations](ch01_foundations/) | Claude 4 — what actually changed |
| I — Foundations | 2 | [ch02_prompt_engineering](ch02_prompt_engineering/) | Prompt engineering for Claude specifically |
| I — Foundations | 3 | [ch03_advanced_prompts](ch03_advanced_prompts/) | Chain-of-thought, few-shot, self-critique loops |
| II — Building with the API | 4 | [ch04_api](ch04_api/) | Streaming, tool use, vision, token budgets |
| II — Building with the API | 5 | [ch05_mcp](ch05_mcp/) | Model Context Protocol |
| II — Building with the API | 6 | [ch06_rag](ch06_rag/) | RAG — embeddings, chunking, hybrid search |
| III — Agentic Architectures | 7 | [ch07_single_agent](ch07_single_agent/) | Single-agent patterns |
| III — Agentic Architectures | 8 | [ch08_multi_agent](ch08_multi_agent/) | Multi-agent orchestration |
| III — Agentic Architectures | 9 | [ch09_production](ch09_production/) | Stateful sessions, human-in-the-loop, cost controls |
| IV — Real-World Projects | 10 | [ch10_research_assistant](ch10_research_assistant/) | AI Research Assistant (end-to-end build) |
| IV — Real-World Projects | 11 | [ch11_data_pipeline](ch11_data_pipeline/) | Multi-Agent Data Analysis Pipeline |
| IV — Real-World Projects | 12 | [ch12_n8n](ch12_n8n/) | Intelligent Workflow Automator with n8n |
| V — Deployment & Security | 13 | [ch13_deployment](ch13_deployment/) | Docker, Cloud Run, scaling |
| V — Deployment & Security | 14 | [ch14_security](ch14_security/) | Prompt injection, PII, audit logging |
| V — Deployment & Security | 15 | [ch15_road_ahead](ch15_road_ahead/) | What's coming and how to build for it |
| — | Appendix | [appendix](appendix/) | 15 production-ready prompt templates |

All scripts are standalone and runnable. The code works — the explanations for *why* it works live in the book.

---

## Setup

### Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone the repo

```bash
git clone https://github.com/MernaHesham/claude-in-production-playbook.git
cd claude-in-production-playbook
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

Or with conda:

```bash
conda create -n claude-prod python=3.11
conda activate claude-prod
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
ANTHROPIC_API_KEY=your-key-here
```

---

## Notable examples

A few files worth jumping to directly:

- **[ch05_mcp/server.py](ch05_mcp/server.py)** — a minimal MCP server that connects Claude to a local tool
- **[ch08_multi_agent/1_orchestrator.py](ch08_multi_agent/1_orchestrator.py)** — orchestrator/subagent pattern with parallel execution
- **[ch09_production/2_human_in_loop.py](ch09_production/2_human_in_loop.py)** — human-in-the-loop gate you can drop into any agent
- **[ch09_production/3_observability.py](ch09_production/3_observability.py)** — logging, tracing, and cost tracking for production agents
- **[ch14_security/prompt_injection.py](ch14_security/prompt_injection.py)** — prompt injection detection and defense patterns

---

## The book

**[Claude in Production](https://seliq-ai.com/seliqopedia/claude-in-production)** — $28

Written the way I wish someone had written it when I first started deploying Claude-powered systems — not "here is the API documentation restated in prose," but "here is the mental model, here is why it matters, and here is the exact code you need."

[![Get the book — $28](https://img.shields.io/badge/Seliq%20AI-Get%20the%20book%20%E2%80%94%20%2428-0A1628?style=for-the-badge&labelColor=0A1628&color=2563EB)](https://seliq-ai.com/seliqopedia/claude-in-production)

---

## License

Code in this repository is provided for educational use. See [LICENSE](LICENSE) for details.
