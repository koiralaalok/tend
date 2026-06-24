# tend/agents/triage.py
"""
Triage agent module for Tend.
Implements concurrent triage using a ParallelAgent for email_1 and email_2,
using custom skill guidelines for action-item extraction, and gathering them.
"""

import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent

MODEL_NAME = "gemini-2.5-flash"


def load_skill_instructions() -> str:
    """Reads and returns the house style skill instructions."""
    # Resolved relative to this file's location
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


# Load the style instructions once
HOUSE_STYLE = load_skill_instructions()

# Triage Agent 1: Classifies and processes email_1
triage_agent_1 = LlmAgent(
    name="TriageAgent1",
    model=MODEL_NAME,
    instruction=f"""
    You are Triage Agent 1.
    Retrieve the email with ID 'email_1' using the `get_message` tool.
    Classify the email as one of: bill, invite, action_needed, fyi, newsletter.
    
    Extract deadlines and action items following these House Style guidelines:
    
    {HOUSE_STYLE}
    
    Output a structured Markdown triage report for email_1.
    """,
    description="Processes and triages email_1 in parallel.",
    output_key="triage_1_output",
)

# Triage Agent 2: Classifies and processes email_2
triage_agent_2 = LlmAgent(
    name="TriageAgent2",
    model=MODEL_NAME,
    instruction=f"""
    You are Triage Agent 2.
    Retrieve the email with ID 'email_2' using the `get_message` tool.
    Classify the email as one of: bill, invite, action_needed, fyi, newsletter.
    
    Extract deadlines and action items following these House Style guidelines:
    
    {HOUSE_STYLE}
    
    Output a structured Markdown triage report for email_2.
    """,
    description="Processes and triages email_2 in parallel.",
    output_key="triage_2_output",
)

# Parallel Triage: Runs triage_agent_1 and triage_agent_2 concurrently
triage_parallel = ParallelAgent(
    name="TriageParallel",
    sub_agents=[triage_agent_1, triage_agent_2],
)

# Gather Agent: Merges the parallel outputs
triage_gather_agent = LlmAgent(
    name="TriageGatherAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Triage Gather Agent.
    Your task is to merge the separate triage outputs from TriageAgent1 and TriageAgent2:
    
    ---
    TriageAgent1 Output:
    {triage_1_output}
    
    TriageAgent2 Output:
    {triage_2_output}
    ---
    
    Combine them into a single, unified Markdown list. Preserve the exact House Style formatting for the action items.
    """,
    description="Gathers and combines concurrent triage reports.",
    output_key="triage_output",
)
