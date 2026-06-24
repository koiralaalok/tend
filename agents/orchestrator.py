# tend/agents/orchestrator.py
"""
Orchestrator for Tend agents.
Coordinates the execution of Triage -> Scheduler -> Drafting -> Briefing agents.
Equips the agents with MCP tool access.
"""

import os
import sys
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

from tend.agents.triage import triage_agent
from tend.agents.scheduler import scheduler_agent
from tend.agents.drafting import drafting_agent
from tend.agents.briefing import briefing_agent

# Resolve the server.py path relative to this project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_script = os.path.join(BASE_DIR, "mcp_server", "server.py")

# Configure the local MCP server toolset using standard I/O connection parameters
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=os.environ.copy(),
        )
    )
)

# Equip Triage, Scheduler, and Drafting agents with the custom MCP tools
triage_agent.tools = [mcp_toolset]
scheduler_agent.tools = [mcp_toolset]
drafting_agent.tools = [mcp_toolset]

# Wire them into the SequentialAgent orchestrator
orchestrator = SequentialAgent(
    name="TendOrchestrator",
    sub_agents=[
        triage_agent,
        scheduler_agent,
        drafting_agent,
        briefing_agent,
    ],
)
