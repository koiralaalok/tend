# tend/agents/scheduler.py
"""
Scheduler agent for Tend.
Responsible for reviewing calendars and scheduling appointments using MCP tools.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

scheduler_agent = LlmAgent(
    name="SchedulerAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Scheduler Agent for Tend.
    
    Your task is to:
    1. Call the `list_events` tool to retrieve current calendar events.
    2. Review the action items and deadlines identified by the Triage Agent:
    
    ---
    {triage_output}
    ---
    
    3. Propose specific, realistic time blocks (date and start/end time) for executing each action item, keeping the deadlines in mind.
    4. Cross-reference your proposals with the retrieved calendar events. If there is a scheduling conflict, flag it clearly (state which events conflict and why).
    
    Output a structured Markdown summary of proposed time blocks and any conflicts detected.
    """,
    description="Manages calendar, schedules action items, and flags conflicts.",
    output_key="scheduler_output"
)
