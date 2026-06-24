# tend/agents/drafting.py
"""
Drafting agent for Tend.
Produces response drafts for incoming messages.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

drafting_agent = LlmAgent(
    name="DraftingAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Drafting Agent for Tend.
    
    Your task is to:
    1. Read the triage results:
    
    ---
    {triage_output}
    ---
    
    2. Identify which emails require a reply (e.g. emails classified as 'action_needed', 'invite', etc.).
    3. Draft a professional, clear, and helpful reply for each. If there is scheduling info (like suggested times), align it with the schedule proposed.
    4. Do not call any tools to send the emails. Just output the drafts.
    
    Output a structured Markdown list of proposed email drafts, clearly labeled with the corresponding Message ID.
    """,
    description="Drafts reply emails for messages requiring response.",
    output_key="drafting_output"
)
