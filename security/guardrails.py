# tend/security/guardrails.py
"""
Security guardrails for Tend.
Implements PII redaction and indirect prompt injection filtering using BasePlugin.
Logs security events for validation reporting.
"""

import re
import logging
from typing import Optional, Dict, Any
from google.adk.runners import BasePlugin
from google.adk.tools.tool_context import ToolContext

# Global registers to track security logs for demo reporting
PII_REDACTIONS = []
INJECTION_DETECTIONS = []


def mask_pii(text: str) -> str:
    """Masks emails, phone numbers, and bank account numbers in text."""
    # 1. Emails
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    text, email_count = re.subn(email_pattern, "[REDACTED_EMAIL]", text)

    # 2. Phone numbers (e.g. +1-234-567-8900 or 123-456-7890)
    phone_pattern = r"\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}"
    text, phone_count = re.subn(phone_pattern, "[REDACTED_PHONE]", text)

    # 3. Account-number-like sequences (10 to 18 digits)
    account_pattern = r"\b\d{10,18}\b"
    text, account_count = re.subn(account_pattern, "[REDACTED_ACCOUNT]", text)

    if email_count > 0 or phone_count > 0 or account_count > 0:
        log_msg = f"Redacted: {email_count} email(s), {phone_count} phone(s), {account_count} account(s)"
        PII_REDACTIONS.append(log_msg)
        logging.info(f"[Security Guardrail] PII Masked: {log_msg}")

    return text


def detect_and_neutralize_injection(body_text: str) -> str:
    """Scans and neutralizes instruction overrides in untrusted text."""
    injection_indicators = [
        "ignore previous instructions",
        "ignore all prior instructions",
        "ignore prior instructions",
        "override previous instructions",
        "delete all instructions",
        "system prompt",
        "do not reply",
        "output the message",
        "injection successful",
    ]

    detected = False
    lower_body = body_text.lower()
    for indicator in injection_indicators:
        if indicator in lower_body:
            detected = True
            break

    if detected:
        log_msg = "Indirect prompt injection signature detected in email body."
        INJECTION_DETECTIONS.append(log_msg)
        logging.warning(f"[Security Guardrail] Prompt Injection Filter Fired: {log_msg}")

        # Cleanse and neutralize triggers in the text
        cleaned_text = body_text
        for indicator in injection_indicators:
            pattern = re.compile(re.escape(indicator), re.IGNORECASE)
            cleaned_text = pattern.sub("[CLEANSED_INJECTION_TRIGGER]", cleaned_text)
        return cleaned_text

    return body_text


class SecurityGuardrailPlugin(BasePlugin):
    """
    Modular plugin that enforces security guardrails (PII redaction and prompt injection checks)
    via ADK model and tool callbacks.
    """

    def __init__(self, name="SecurityGuardrail"):
        super().__init__(name=name)

    async def before_model_callback(self, *, callback_context, llm_request) -> None:
        """Masks PII in the model request payload before sending it to the LLM."""
        if llm_request.contents:
            for content in llm_request.contents:
                if content.parts:
                    for part in content.parts:
                        if part.text:
                            part.text = mask_pii(part.text)
        return None

    async def after_tool_callback(
        self, *, tool, tool_args, tool_context, result
    ) -> Optional[dict]:
        """Intercepts the output of get_message and sanitizes indirect prompt injections."""
        if tool.name == "get_message" and "body" in result:
            result["body"] = detect_and_neutralize_injection(result["body"])
        return result
