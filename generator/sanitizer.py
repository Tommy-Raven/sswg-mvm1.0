from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping

SENSITIVE_KEYS = (
    "password",
    "secret",
    "token",
    "api_key",
    "credential",
    "private_key",
)

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP)? PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]"),
    re.compile(r"(?i)api[_-]?key\s*[:=]"),
    re.compile(r"(?i)token\s*[:=]"),
    re.compile(r"(?i)password\s*[:=]"),
    re.compile(r"(?i)secret\s*[:=]"),
]

HIGH_ENTROPY_PATTERN = re.compile(r"[A-Za-z0-9+/=_-]{20,}")

MAX_STRING_LENGTH = 256
HIGH_ENTROPY_THRESHOLD = 4.0


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _truncate(value: str) -> str:
    if len(value) <= MAX_STRING_LENGTH:
        return value
    return value[:MAX_STRING_LENGTH] + "...[TRUNCATED]"


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    for token in HIGH_ENTROPY_PATTERN.findall(redacted):
        if shannon_entropy(token) >= HIGH_ENTROPY_THRESHOLD:
            redacted = redacted.replace(token, "[REDACTED]")
    return _truncate(redacted)


def find_secret_indicators(value: str) -> list[str]:
    indicators: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            indicators.append(pattern.pattern)
    for token in HIGH_ENTROPY_PATTERN.findall(value):
        if shannon_entropy(token) >= HIGH_ENTROPY_THRESHOLD:
            indicators.append("high_entropy")
            break
    return indicators


def _sanitize_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(token in key_lower for token in SENSITIVE_KEYS):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = sanitize_payload(value)
    return sanitized


def _sanitize_iterable(values: Iterable[Any]) -> list[Any]:
    return [sanitize_payload(value) for value in values]


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _sanitize_mapping(value)
    if isinstance(value, (list, tuple)):
        return _sanitize_iterable(value)
    if isinstance(value, str):
        return redact_text(value)
    return value
