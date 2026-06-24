# tend/agents/briefing.py
"""
Briefing agent for Tend.
Responsible for presenting actions taken and notifications as a structured briefing.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

briefing_agent = LlmAgent(
    name="BriefingAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Briefing Agent for Tend.
    Compile a high-level briefing summarizing the triage outcomes, schedule changes, and prepared drafts.
    """,
    description="Compiles structured summaries of actions taken by the concierge."
)
