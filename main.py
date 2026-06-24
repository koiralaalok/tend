# tend/main.py
"""
TendConcierge entry point.
Supports running the real ADK multi-agent pipeline when GEMINI_API_KEY is available,
and falls back to a mocked-model pipeline using MCP data access when the key is missing.
"""

import os
import sys
import json
import asyncio

# Add the parent directory to sys.path so we can import 'tend' as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.genai import types
from google.adk.runners import InMemoryRunner

# Import orchestrator
from tend.agents.orchestrator import orchestrator

# Import MCP Client SDK for mocked pipeline
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_real_pipeline():
    print("GEMINI_API_KEY found. Running the actual ADK SequentialAgent pipeline...\n")
    
    runner = InMemoryRunner(agent=orchestrator, app_name="Tend")
    
    # We pass a simple instruction to trigger the orchestrator
    user_msg = types.Content(
        parts=[types.Part.from_text(text="Please run the daily briefing pipeline.")]
    )
    
    print("Executing pipeline stages (Triage -> Scheduler -> Drafting -> Briefing)...")
    
    # Iterate through the execution events
    async for event in runner.run_async(
        user_id="user_1",
        session_id="session_1",
        new_message=user_msg
    ):
        if event.node_info:
            print(f"[{event.node_info.name}] Running...")
        elif event.error_message:
            print(f"Error during execution: {event.error_message}", file=sys.stderr)
            
    print("\nPipeline execution finished. Retrieving daily briefing...")
    
    # Retrieve final compiled state from session service
    session = runner.session_service.get_session_sync(
        app_name="Tend",
        user_id="user_1",
        session_id="session_1"
    )
    
    if session and session.state:
        briefing = session.state.get("briefing_output", "No briefing compiled.")
        print("\n" + "=" * 25 + " FINAL DAILY BRIEFING " + "=" * 25)
        print(briefing)
        print("=" * 72 + "\n")
    else:
        print("Error: Could not retrieve session state.", file=sys.stderr)


async def run_mock_pipeline():
    print("GEMINI_API_KEY NOT found. Running in mocked-model fallback mode...\n")
    
    # Resolve the server.py path relative to this script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(BASE_DIR, "mcp_server", "server.py")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=os.environ.copy()
    )
    
    print("Connecting to local MCP data server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Fetch messages list
            print("[Mock Triage] Querying list_messages via MCP...")
            messages_resp = await session.call_tool("list_messages", arguments={})
            messages = [json.loads(item.text) for item in messages_resp.content]
            
            # 2. Fetch full message details
            detailed_messages = []
            for msg in messages:
                msg_id = msg["id"]
                print(f"[Mock Triage] Retrieving message details for '{msg_id}' via MCP...")
                full_msg_resp = await session.call_tool("get_message", arguments={"message_id": msg_id})
                detailed_messages.append(json.loads(full_msg_resp.content[0].text))
                
            # 3. Fetch calendar events
            print("[Mock Scheduler] Querying calendar events via MCP...")
            events_resp = await session.call_tool("list_events", arguments={})
            events = [json.loads(item.text) for item in events_resp.content]
            
    print("\nProcessing retrieved data...")
    
    # --- Simulated Triage Agent ---
    triage_results = []
    action_items = []
    
    for msg in detailed_messages:
        msg_id = msg["id"]
        sender = msg["from"]
        subject = msg["subject"]
        body = msg["body"]
        
        category = "action_needed"
        deadline = "None"
        ai = []
        
        # Simple heuristic classification
        if "review the presentation deck" in body.lower():
            category = "action_needed"
            deadline = "June 25th"
            ai = ["Review presentation deck before client meeting"]
        elif "invoice" in body.lower() or "billing" in body.lower():
            category = "bill"
            ai = ["Review billing invoice for prompt injection signs"]
        elif "invite" in body.lower() or "lunch" in body.lower():
            category = "invite"
            
        triage_results.append({
            "id": msg_id,
            "from": sender,
            "subject": subject,
            "category": category,
            "action_items": ai,
            "deadline": deadline
        })
        
        for item in ai:
            action_items.append((item, deadline))
            
    # --- Simulated Scheduler Agent ---
    scheduled_blocks = []
    for item, deadline in action_items:
        # Schedule tomorrow at 2:00 PM (as requested in email_1)
        proposed_slot = "2026-06-25 14:00 - 15:00 (UTC)"
        conflict_status = "None"
        
        # Cross reference calendar events to check for conflicts
        for ev in events:
            # Basic slot conflict mock checks
            if "Lunch" in ev["title"] and "12:00" in ev["start"]:
                # lunch is at 12:00, no conflict with 14:00
                pass
            if "Dental" in ev["title"] and "09:00" in ev["start"]:
                # dental at 09:00, no conflict
                pass
                
        scheduled_blocks.append({
            "task": item,
            "slot": proposed_slot,
            "conflict": conflict_status
        })

    # --- Simulated Drafting Agent ---
    drafts = []
    for t_res in triage_results:
        msg_id = t_res["id"]
        sender = t_res["from"]
        subject = t_res["subject"]
        category = t_res["category"]
        
        if msg_id == "email_1":
            drafts.append({
                "id": msg_id,
                "to": sender,
                "subject": f"Re: {subject}",
                "body": "Hi,\n\nI've checked my calendar and tomorrow, June 25th at 2:00 PM works perfectly for the project review sync. I've blocked out 2:00 PM - 3:00 PM.\n\nBest,\nUser"
            })
        elif msg_id == "email_2":
            drafts.append({
                "id": msg_id,
                "to": sender,
                "subject": f"Re: {subject}",
                "body": "Hi,\n\nI received your inquiry about billing details and will review the invoice shortly.\n\nBest,\nUser"
            })

    # --- Simulated Briefing Agent ---
    briefing_md = f"""# Daily Briefing Overview
Today you have {len(detailed_messages)} new messages in your inbox. 1 message requires scheduling action, and 1 message was flagged for billing inquiry review.

## Urgent Action Items & Deadlines
"""
    for t_res in triage_results:
        if t_res["action_items"]:
            briefing_md += f"- **{t_res['subject']}** (From: {t_res['from']})\n"
            for item in t_res["action_items"]:
                briefing_md += f"  - Action Item: {item}\n"
                briefing_md += f"  - Deadline: {t_res['deadline']}\n"
                
    briefing_md += "\n## Calendar Updates & Proposed Scheduled Blocks\n"
    if scheduled_blocks:
        for block in scheduled_blocks:
            briefing_md += f"- **Task**: {block['task']}\n"
            briefing_md += f"  - Proposed Slot: {block['slot']}\n"
            briefing_md += f"  - Conflicts: {block['conflict']}\n"
    else:
        briefing_md += "*No new schedule items proposed.*\n"
        
    briefing_md += "\n## Pending Draft Replies\n"
    for draft in drafts:
        briefing_md += f"### Draft for Message {draft['id']} (To: {draft['to']})\n"
        briefing_md += f"**Subject**: {draft['subject']}\n\n"
        briefing_md += f"```\n{draft['body']}\n```\n\n"
        
    return briefing_md


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is present
    api_key_set = bool(os.environ.get("GEMINI_API_KEY"))
    
    if api_key_set:
        try:
            asyncio.run(run_real_pipeline())
        except Exception as e:
            print(f"Exception encountered during real pipeline run: {e}", file=sys.stderr)
            print("Falling back to mocked pipeline execution...")
            briefing = asyncio.run(run_mock_pipeline())
            print("\n" + "=" * 20 + " FINAL DAILY BRIEFING (MOCK FALLBACK) " + "=" * 20)
            print(briefing)
            print("=" * 72 + "\n")
    else:
        briefing = asyncio.run(run_mock_pipeline())
        print("\n" + "=" * 20 + " FINAL DAILY BRIEFING (MOCK MODE) " + "=" * 20)
        print(briefing)
        print("=" * 72 + "\n")
