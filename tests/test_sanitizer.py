from __future__ import annotations

from generator.sanitizer import redact_text, sanitize_payload
from tests.assertions import require


def test_redact_text_masks_secrets_and_truncates() -> None:
    secret = "sk-" + ("A" * 30)
    long_text = "a" * 300
    combined = f"{secret} {long_text}"
    redacted = redact_text(combined)
    require("[REDACTED]" in redacted, "Expected secret to be redacted")
    require(
        redacted.endswith("...[TRUNCATED]"),
        "Expected long text to be truncated",
    )


def test_sanitize_payload_redacts_sensitive_keys() -> None:
    payload = {"token": "secret", "nested": {"password": "value"}}
    sanitized = sanitize_payload(payload)
    require(sanitized["token"] == "[REDACTED]", "Expected token to be redacted")
    require(
        sanitized["nested"]["password"] == "[REDACTED]",
        "Expected password to be redacted",
    )
