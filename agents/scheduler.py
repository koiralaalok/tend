# tend/agents/scheduler.py
"""
Scheduler agent for Tend.
Responsible for reviewing calendars and scheduling appointments or meetings.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

scheduler_agent = LlmAgent(
    name="SchedulerAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Scheduler Agent for Tend.
    Identify calendar requests, detect scheduling conflicts, and suggest times/dates.
    """,
    description="Manages calendar and schedules meetings/events."
)
