import re


_WHITESPACE_RE = re.compile(r"\s+")
_SAFE_PUNCT_RE = re.compile(r"[^\w\s\-/]")


def normalize_text(text: str) -> str:
    lowered = (text or "").lower().strip()
    sanitized = _SAFE_PUNCT_RE.sub(" ", lowered)
    normalized = _WHITESPACE_RE.sub(" ", sanitized)
    return normalized
