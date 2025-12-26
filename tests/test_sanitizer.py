from __future__ import annotations

from generator.sanitizer import redact_text, sanitize_payload


def test_redact_text_masks_secrets_and_truncates() -> None:
    secret = "sk-ABCDEFGHIJKLMNOPQRSTUV0123456789"
    long_text = "a" * 300
    combined = f"{secret} {long_text}"
    redacted = redact_text(combined)
    assert "[REDACTED]" in redacted
    assert redacted.endswith("...[TRUNCATED]")


def test_sanitize_payload_redacts_sensitive_keys() -> None:
    payload = {"token": "secret", "nested": {"password": "value"}}
    sanitized = sanitize_payload(payload)
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["nested"]["password"] == "[REDACTED]"
