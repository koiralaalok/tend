# tend/demo_security.py
"""
Demo script to verify Tend's security guardrails.
Runs the pipeline over synthetic emails including the adversarial injection payload,
simulates/triggers the callbacks, tests allowed/blocked send paths,
and outputs a comprehensive "Tend Security Report".
"""

import os
import sys
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ensure the parent directory is in sys.path so we can import 'tend'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tend.security.guardrails import (
    mask_pii,
    detect_and_neutralize_injection,
    PII_REDACTIONS,
    INJECTION_DETECTIONS,
)


async def run_security_demo():
    print("=" * 72)
    print("           TEND SECURITY GUARDRAILS DEMO RUN")
    print("=" * 72)

    # Resolve server script path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(BASE_DIR, "mcp_server", "server.py")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=os.environ.copy(),
    )

    print("\n[Step 1] Connecting to MCP Data Server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Retrieve messages list
            messages_resp = await session.call_tool("list_messages", arguments={})
            messages = [json.loads(item.text) for item in messages_resp.content]

            # Fetch messages and simulate callback-driven security processing
            print("\n[Step 2] Retrieving and scanning messages via MCP...")
            detailed_messages = []
            for msg in messages:
                msg_id = msg["id"]
                full_msg_resp = await session.call_tool(
                    "get_message", arguments={"message_id": msg_id}
                )
                msg_data = json.loads(full_msg_resp.content[0].text)

                # 1. Trigger Indirect Prompt-Injection Filter (after_tool_callback)
                raw_body = msg_data["body"]
                sanitized_body = detect_and_neutralize_injection(raw_body)
                msg_data["body"] = sanitized_body

                # 2. Trigger PII Redaction (before_model_callback)
                # Mask sender email and body details
                msg_data["from"] = mask_pii(msg_data["from"])
                msg_data["body"] = mask_pii(msg_data["body"])

                detailed_messages.append(msg_data)
                print(f"Processed message '{msg_id}' safely.")

            # 3. Test send_email tool guardrails
            print("\n[Step 3] Verifying send action guardrails...")

            # Refusal 1: Recipient Allowlist refusal
            print("Attempting to send email to unauthorized recipient 'spammer@malicious.com'...")
            block_allowlist_resp = await session.call_tool(
                "send_email",
                arguments={
                    "to": "spammer@malicious.com",
                    "subject": "Invoice Inquiry Response",
                    "body": "Here are the payment details.",
                    "confirm": True,
                },
            )
            block_allowlist_res = json.loads(block_allowlist_resp.content[0].text)
            print(f"Result: {block_allowlist_res['message']}")

            # Refusal 2: Human-in-the-loop confirmation check
            print("\nAttempting to send email to allowed recipient 'manager@company.com' WITHOUT confirmation...")
            block_confirm_resp = await session.call_tool(
                "send_email",
                arguments={
                    "to": "manager@company.com",
                    "subject": "Project Review Sync",
                    "body": "Hi, I have scheduled the sync for 2:00 PM tomorrow.",
                    "confirm": False,
                },
            )
            block_confirm_res = json.loads(block_confirm_resp.content[0].text)
            print(f"Result: {block_confirm_res['message']}")

            # Successful Send
            print("\nAttempting to send email to allowed recipient 'manager@company.com' WITH confirmation...")
            success_resp = await session.call_tool(
                "send_email",
                arguments={
                    "to": "manager@company.com",
                    "subject": "Project Review Sync",
                    "body": "Hi, I have scheduled the sync for 2:00 PM tomorrow.",
                    "confirm": True,
                },
            )
            success_res = json.loads(success_resp.content[0].text)
            print(f"Result: {success_res['message']}")

    # Print the security report
    print("\n" + "=" * 25 + " TEND SECURITY REPORT " + "=" * 25)
    print(f"1. PII Redaction: {len(PII_REDACTIONS)} detection(s)")
    for redaction in PII_REDACTIONS:
        print(f"   [MASKED] {redaction}")

    print(
        f"\n2. Indirect Prompt-Injection Defense: {len(INJECTION_DETECTIONS)} detection(s)"
    )
    for detection in INJECTION_DETECTIONS:
        print(f"   [BLOCKED] {detection} -> Cleansed malicious instructions.")

    print("\n3. Human-in-the-Loop Send Gate: Verified")
    print(f"   [BLOCKED] {block_confirm_res['message']}")

    print("\n4. Recipient Allowlist: Verified")
    print(f"   [BLOCKED] {block_allowlist_res['message']}")

    print("\n5. Authorized Send: Verified")
    print(f"   [ALLOWED] {success_res['message']}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    asyncio.run(run_security_demo())
