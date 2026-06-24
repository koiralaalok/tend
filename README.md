# Tend — Privacy-First Life-Admin Concierge

Tend is a privacy-first life-admin concierge built as a Capstone project for the Kaggle Concierge track. It processes incoming personal emails, schedules action items on a calendar, drafts response drafts, and compiles a daily briefing.

## 1. Problem Statement & Architecture
- **Problem**: AI agents require access to highly sensitive personal data (emails, calendar) to manage life-admin. This exposes users to major risks of data exfiltration, unauthorized actions (e.g. sending emails autonomously), and indirect prompt injection attacks (where emails contain hidden instructions that hijack the agent).
- **Architecture**: Tend uses a strict multi-agent pipeline orchestrated sequentially. Personal data is never read directly from the disk; it is accessed only through a custom MCP server which filters out internal metadata. A dedicated security plugin screens LLM payloads and tool responses, while the action layer enforces human confirmation and recipient allowlists.

## 2. Core Concepts Mapping
This project explicitly implements four core agent development concepts:
1. **Multi-Agent ADK**: Sequential orchestration running parallel triage classifiers (`ParallelAgent`) and a self-reviewing briefing refinement loop (`LoopAgent`).
   - *Code pointer*: [`agents/orchestrator.py`](file:///c:/Users/alokk/agy2-projects/google-cloud-serverless-app/tend/agents/orchestrator.py)
2. **Custom MCP Data Server**: A read-only data boundary serving messages and calendar events while redacting evaluation flags.
   - *Code pointer*: [`mcp_server/server.py`](file:///c:/Users/alokk/agy2-projects/google-cloud-serverless-app/tend/mcp_server/server.py)
3. **Custom Agent Skill**: Enforces action-item extraction structures and reply tone templates.
   - *Code pointer*: [`skills/house_style/SKILL.md`](file:///c:/Users/alokk/agy2-projects/google-cloud-serverless-app/tend/skills/house_style/SKILL.md)
4. **Security Guardrails**: Implements PII redaction, indirect prompt injection defense, a recipient allowlist, and a human confirmation gate.
   - *Code pointer*: [`security/guardrails.py`](file:///c:/Users/alokk/agy2-projects/google-cloud-serverless-app/tend/security/guardrails.py) and [`mcp_server/server.py`](file:///c:/Users/alokk/agy2-projects/google-cloud-serverless-app/tend/mcp_server/server.py)

## 3. Quickstart (Local Execution)

### Setup
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution
- Run the main pipeline (triage, scheduling, drafting, briefing):
  ```bash
  python main.py
  ```
- Run the security demo script:
  ```bash
  python demo_security.py
  ```
