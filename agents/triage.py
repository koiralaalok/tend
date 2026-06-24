# tend/agents/triage.py
"""
Triage agent for Tend.
Responsible for reading and categorizing incoming messages.
"""

from google.adk.agents.llm_agent import LlmAgent

# Model ID to use (falls back to mocked execution if GEMINI_API_KEY is not set)
MODEL_NAME = "gemini-2.5-flash"

triage_agent = LlmAgent(
    name="TriageAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Triage Agent for Tend.
    Analyze incoming emails and messages, categorize them, and flag urgent tasks.
    """,
    description="Analyzes and categorizes incoming messages."
)
