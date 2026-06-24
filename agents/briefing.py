# tend/agents/briefing.py
"""
Briefing agent for Tend.
Compiles a formatted Markdown summary of the daily triage, schedule, and draft replies.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

briefing_agent = LlmAgent(
    name="BriefingAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Briefing Agent for Tend.
    
    Your task is to compile a daily briefing in Markdown format.
    Use the outputs from the previous agents in the pipeline:
    
    ---
    Triage Output:
    {triage_output}
    
    Scheduler Output:
    {scheduler_output}
    
    Drafting Output:
    {drafting_output}
    ---
    
    Assemble them into a beautiful, coherent daily summary for the user. Include:
    - Daily Briefing Overview (a short intro of today's workload).
    - Urgent Action Items & Deadlines.
    - Calendar Updates & Proposed Scheduled Blocks (including any conflicts).
    - Pending Draft Replies.
    """,
    description="Assembles and formats the final Markdown daily briefing.",
    output_key="briefing_output"
)
