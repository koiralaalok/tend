# tend/agents/briefing.py
"""
Briefing agent module for Tend.
Implements a self-reviewing loop using a LoopAgent, with a writer agent,
a critic agent, and an exiter tool.
"""

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.tools.tool_context import ToolContext

MODEL_NAME = "gemini-2.5-flash"


def exit_loop(tool_context: ToolContext) -> dict:
    """
    Call this tool ONLY when the briefing meets all formatting and quality criteria,
    signaling the iterative review loop to terminate.
    """
    print("  [Tool Call] exit_loop triggered: briefing meets all criteria.")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}


# 1. Writer Agent: Compiles or refines the briefing draft
briefing_writer_agent = LlmAgent(
    name="BriefingWriterAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Briefing Writer Agent.
    
    Your task is to compile a daily briefing in Markdown format based on:
    - Triage Output: {triage_output}
    - Scheduler Output: {scheduler_output}
    - Drafting Output: {drafting_output}
    
    If there is prior criticism from the Critic Agent in {briefing_critique}, use it to refine the draft:
    ---
    Critic Feedback:
    {briefing_critique}
    ---
    Otherwise, write the initial draft.
    
    Ensure your briefing includes these exact sections:
    1. Daily Briefing Overview
    2. Urgent Action Items & Deadlines
    3. Calendar Updates & Proposed Scheduled Blocks
    4. Pending Draft Replies
    
    Output *only* the daily briefing markdown.
    """,
    description="Compiles and refines the daily briefing.",
    output_key="briefing_output",
)

# 2. Critic Agent: Evaluates the draft and calls exit_loop if complete
briefing_critic_agent = LlmAgent(
    name="BriefingCriticAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Briefing Critic Agent.
    Review the current daily briefing draft:
    
    ---
    {briefing_output}
    ---
    
    Verify that the briefing contains all of the following:
    1. A 'Daily Briefing Overview' section.
    2. An 'Urgent Action Items & Deadlines' section.
    3. A 'Calendar Updates & Proposed Scheduled Blocks' section.
    4. A 'Pending Draft Replies' section.
    
    If ALL criteria are met and the briefing is complete, call the `exit_loop` tool immediately to finish the loop.
    
    If any criteria are missing or incomplete, output specific, constructive criticism detailing what needs to be added or changed.
    Do NOT call `exit_loop` if criteria are missing.
    """,
    description="Critiques the briefing draft and calls exit_loop on completion.",
    tools=[exit_loop],
    output_key="briefing_critique",
)

# 3. Loop Agent: Manages the writer/critic loop
briefing_loop = LoopAgent(
    name="BriefingLoop",
    sub_agents=[briefing_writer_agent, briefing_critic_agent],
    max_iterations=3,
)
