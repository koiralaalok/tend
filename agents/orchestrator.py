# tend/agents/orchestrator.py
"""
Orchestrator for Tend agents.
Coordinates the execution of:
TriageParallel -> TriageGatherAgent -> SchedulerAgent -> DraftingAgent -> BriefingLoop.
"""

import os
import sys
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

# Import sub-agents
from tend.agents.triage import triage_parallel, triage_agent_1, triage_agent_2, triage_gather_agent
from tend.agents.scheduler import scheduler_agent
from tend.agents.drafting import drafting_agent
from tend.agents.briefing import briefing_loop, briefing_writer_agent, briefing_critic_agent

# Resolve the server.py path relative to this project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_script = os.path.join(BASE_DIR, "mcp_server", "server.py")

# Configure the local MCP server toolset
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=os.environ.copy(),
        )
    )
)

# Equip the appropriate LLM sub-agents with MCP tools
triage_agent_1.tools = [mcp_toolset]
triage_agent_2.tools = [mcp_toolset]
scheduler_agent.tools = [mcp_toolset]
drafting_agent.tools = [mcp_toolset]

# Wire all stages into a SequentialAgent orchestrator
orchestrator = SequentialAgent(
    name="TendOrchestrator",
    sub_agents=[
        triage_parallel,
        triage_gather_agent,
        scheduler_agent,
        drafting_agent,
        briefing_loop,
    ],
)
