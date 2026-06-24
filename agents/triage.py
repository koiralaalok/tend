# tend/agents/triage.py
"""
Triage agent for Tend.
Responsible for reading and categorizing incoming messages using MCP tools.
"""

from google.adk.agents.llm_agent import LlmAgent

MODEL_NAME = "gemini-2.5-flash"

triage_agent = LlmAgent(
    name="TriageAgent",
    model=MODEL_NAME,
    instruction="""
    You are the Triage Agent for Tend.
    
    Your task is to:
    1. Call the `list_messages` tool to get the list of recent email summaries.
    2. For each message retrieved, call the `get_message` tool using its `message_id` to get the full email body.
    3. Categorize each email into exactly one of these classes:
       - bill (invoices, payment requests)
       - invite (calendar events, meetings, social invites)
       - action_needed (requires user response or task execution)
       - fyi (informational, no direct action required)
       - newsletter (automated newsletters, updates)
    4. Extract any deadlines, dates, and clear action items from the emails.
    
    Output a structured Markdown summary listing each message's ID, sender, subject, category, action items, and deadlines.
    """,
    description="Reads inbox messages, categorizes them, and extracts deadlines and action items.",
    output_key="triage_output"
)
