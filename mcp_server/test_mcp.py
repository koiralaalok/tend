# tend/mcp_server/test_mcp.py
"""
Integration test for the Tend custom MCP server.
Uses stdio_client to launch the server as a subprocess and tests each tool.
"""

import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    print("Starting MCP server integration test...")

    # Resolve server.py path relative to this script
    server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "server.py"
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=os.environ.copy(),
    )

    print(f"Server script path: {server_script}")
    print(f"Python executable: {sys.executable}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("MCP Session initialized successfully.")

            # 1. List tools
            tools_response = await session.list_tools()
            tools = [tool.name for tool in tools_response.tools]
            print(f"\n[1/5] Available Tools: {tools}")
            assert "list_messages" in tools
            assert "get_message" in tools
            assert "list_events" in tools

            # 2. Call list_messages
            print("\n[2/5] Calling 'list_messages'...")
            messages = await session.call_tool("list_messages", arguments={})
            print(f"Response:\n{messages.content[0].text}")

            # 3. Call get_message for 'email_1'
            print("\n[3/5] Calling 'get_message' for 'email_1'...")
            msg1 = await session.call_tool(
                "get_message", arguments={"message_id": "email_1"}
            )
            print(f"Response:\n{msg1.content[0].text}")
            assert "category" not in msg1.content[0].text
            assert "injection" not in msg1.content[0].text

            # 4. Call get_message for 'email_2'
            print("\n[4/5] Calling 'get_message' for 'email_2'...")
            msg2 = await session.call_tool(
                "get_message", arguments={"message_id": "email_2"}
            )
            print(f"Response:\n{msg2.content[0].text}")
            assert "category" not in msg2.content[0].text
            assert "injection" not in msg2.content[0].text

            # 5. Call list_events
            print("\n[5/5] Calling 'list_events'...")
            events = await session.call_tool("list_events", arguments={})
            print(f"Response:\n{events.content[0].text}")

            print("\nMCP server verification test completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
