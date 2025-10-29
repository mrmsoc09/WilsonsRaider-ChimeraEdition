"""Utilities to reduce prompt-injection risk and handle untrusted content.
- Never mix control instructions with untrusted data; always pass untrusted as data fields.
- Provide basic sanitization and provenance tagging.
"""
from __future__ import annotations
from typing import Dict
import re

DANGEROUS_PATTERNS = [
    r"(?i)ignore previous instructions",
    r"(?i)disregard above",
    r"(?i)system prompt",
    r"(?i)reveal secrets",
]

def sanitize_untrusted(text: str) -> str:
    clean = text
    for pat in DANGEROUS_PATTERNS:
        clean = re.sub(pat, "[redacted]", clean)
    return clean

def package_untrusted(content: str, source: str) -> Dict:
    return {"provenance": source, "sanitized": sanitize_untrusted(content)}
