# tend/agents/orchestrator.py
"""
Orchestrator for Tend agents.
Coordinates the execution of Triage -> Scheduler -> Drafting -> Briefing agents.
"""

from google.adk.agents.sequential_agent import SequentialAgent
from tend.agents.triage import triage_agent
from tend.agents.scheduler import scheduler_agent
from tend.agents.drafting import drafting_agent
from tend.agents.briefing import briefing_agent

# Stub for the SequentialAgent orchestrator
# In the next milestones, this orchestrator will run the sub-agents sequentially.
orchestrator = SequentialAgent(
    name="TendOrchestrator",
    sub_agents=[
        triage_agent,
        scheduler_agent,
        drafting_agent,
        briefing_agent,
    ]
)
