# tend/agents/drafting.py
"""
Drafting agent for Tend.
Produces response drafts for incoming messages using custom reply tone templates.
"""

import os
from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"


def load_skill_instructions() -> str:
    """Reads and returns the house style skill instructions."""
    skill_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills",
        "house_style",
        "SKILL.md",
    )
    if not os.path.exists(skill_path):
        return ""
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


HOUSE_STYLE = load_skill_instructions()

drafting_agent = LlmAgent(
    name="DraftingAgent",
    model=MODEL_NAME,
    instruction=f"""
    You are the Drafting Agent for Tend.
    
    Your task is to:
    1. Read the unified triage results:
    
    ---
    {{triage_output}}
    ---
    
    2. Identify which emails require a reply (e.g. action_needed, invite, bill, etc.).
    3. Draft a response for each of these emails by selecting the appropriate template and tone from the House Style guidelines:
    
    {HOUSE_STYLE}
    
    Match the reply types (polite decline, confirm/accept, ask-for-more-info) to the message context.
    4. Do not call any tools to send the emails. Just output the drafts.
    
    Output a structured Markdown list of proposed email drafts, clearly labeled with the corresponding Message ID.
    """,
    description="Drafts reply emails matching the house-style tone templates.",
    output_key="drafting_output",
)
