import re
from html import escape


def xml_escape(value: object) -> str:
    return escape(str(value or ""), quote=True)


def truncate(value: str, length: int) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= length else value[: max(0, length - 1)].rstrip() + "…"


def safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", value)


def format_number(value: int) -> str:
    if value < 1_000:
        return str(value)
    if value < 1_000_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "k"
    return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"

