# tend/mcp_server/server.py
"""
MCP Server for Tend.
Exposes tools for reading personal email inbox data and calendar entries.
"""

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("TendPersonalDataServer")

@mcp.tool()
def get_emails() -> str:
    """
    Fetch synthetic personal emails from the inbox.
    """
    # Stub implementation. In subsequent milestones, this will read data/inbox/*.json
    return "[]"

@mcp.tool()
def get_calendar() -> str:
    """
    Fetch synthetic personal calendar events.
    """
    # Stub implementation. In subsequent milestones, this will read data/calendar.json
    return "[]"

if __name__ == "__main__":
    mcp.run()
