# Tend — Privacy-First Life-Admin Concierge

Tend is an agentic, privacy-first life-admin concierge built as a Capstone project for a Kaggle competition (Concierge track).

## Repo Structure
- `agents/`: Contains the SequentialAgent orchestrator and agent definitions (Triage, Scheduler, Drafting, Briefing).
- `mcp_server/`: Contains the MCP server implementation.
- `skills/`: Contains the custom Agent Skill (`house_style/SKILL.md`) encoding action-item extraction guidelines and reply tone.
- `security/`: Contains the guardrail components including PII redaction, indirect prompt injection filters, and a recipient allowlist.
- `data/`: Contains synthetic data (inbox and calendar) to ensure local, reproducible testing.

## Execution Flow
The orchestrator executes the agents sequentially:
1. **Triage**: Categorizes incoming messages and identifies urgency.
2. **Scheduler**: Manages calendar conflicts and schedules events.
3. **Drafting**: Prepares responses based on the triage output and style guidelines.
4. **Briefing**: Compiles a summary/briefing of the current state and actions taken.
