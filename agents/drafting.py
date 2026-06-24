# tend/agents/drafting.py
"""
Drafting agent for Tend.
Responsible for drafting email responses.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

drafting_agent = LlmAgent(
    name="DraftingAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Drafting Agent for Tend.
    Draft reply emails following the house style guidelines.
    """,
    description="Drafts reply emails based on incoming messages and style constraints."
)
