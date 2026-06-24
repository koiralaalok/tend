# tend/security/guardrails.py
"""
Security guardrails for Tend.
Implements PII redaction, prompt injection filtering, human-in-the-loop gates, and recipient allowlist verification.
"""

from google.adk.plugins.base_plugin import BasePlugin

class SecurityGuardrailPlugin(BasePlugin):
    """
    Security plugin to enforce safety guidelines across the Tend agent pipeline.
    """
    # Stub implementation. In subsequent milestones, we will implement lifecycle callbacks
    # for input sanitization, PII redaction, allowlist verification, etc.
    pass
