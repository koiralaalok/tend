# tend/mcp_server/server.py
"""
MCP Server for Tend.
Exposes read-only tools to list and retrieve synthetic emails and calendar events.
Ensures internal evaluation metrics (category, injection flags) are never leaked.
"""

import os
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("TendPersonalDataServer")

# Resolve directories relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INBOX_DIR = os.path.join(DATA_DIR, "inbox")
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.json")


@mcp.tool()
def list_messages(filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List summaries of emails in the inbox.

    Args:
        filter_query: Optional search string to filter messages by sender, subject, or body.
    """
    messages = []
    if not os.path.exists(INBOX_DIR):
        return messages

    for filename in os.listdir(INBOX_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(INBOX_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Apply filtering if filter_query is provided
                    if filter_query:
                        q = filter_query.lower()
                        subject = data.get("subject", "").lower()
                        body = data.get("body", "").lower()
                        sender = data.get("from", "").lower()
                        if q not in subject and q not in body and q not in sender:
                            continue

                    # Construct message summary, omitting ground-truth category/injection
                    summary = {
                        "id": data.get("id"),
                        "from": data.get("from"),
                        "subject": data.get("subject"),
                        "date": data.get("date"),
                    }
                    messages.append(summary)
            except Exception:
                pass

    # Sort messages by date descending (latest first)
    messages.sort(key=lambda x: x.get("date", ""), reverse=True)
    return messages


@mcp.tool()
def get_message(message_id: str) -> Dict[str, Any]:
    """
    Retrieve full details of a specific message by its ID.

    Args:
        message_id: The unique ID of the message to retrieve.
    """
    if not os.path.exists(INBOX_DIR):
        return {"error": "Inbox directory not found."}

    for filename in os.listdir(INBOX_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(INBOX_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("id") == message_id:
                        # Exclude ground-truth label keys to prevent leakage
                        return {
                            "id": data.get("id"),
                            "from": data.get("from"),
                            "to": data.get("to"),
                            "subject": data.get("subject"),
                            "date": data.get("date"),
                            "body": data.get("body"),
                        }
            except Exception:
                pass

    return {"error": f"Message with ID '{message_id}' not found."}


@mcp.tool()
def list_events(date_range: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve a list of calendar events.

    Args:
        date_range: Optional string parameter to filter events by a date range descriptor.
    """
    if not os.path.exists(CALENDAR_FILE):
        return []

    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
            # In subsequent milestones, we can implement sophisticated date range filtering if needed.
            return events
    except Exception:
        return []
ALLOWLIST = ["manager@company.com", "user@tend.local"]


@mcp.tool()
def send_email(
    to: str, subject: str, body: str, confirm: bool = False
) -> Dict[str, Any]:
    """
    Send an email. Requires recipient allowlist validation and human confirmation.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email content body.
        confirm: Confirmation flag. Must be explicitly set to True by a human to authorize sending.
    """
    if to not in ALLOWLIST:
        return {
            "status": "error",
            "message": f"Blocked: Recipient '{to}' is not in the configured allowlist.",
        }

    if not confirm:
        return {
            "status": "error",
            "message": "Blocked: Send action requires explicit human-in-the-loop confirmation (confirm=True).",
        }

    return {
        "status": "success",
        "message": f"Email successfully sent to {to}.",
    }


if __name__ == "__main__":
    mcp.run()
