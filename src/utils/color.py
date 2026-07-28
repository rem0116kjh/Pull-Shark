import re

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")


def normalize_hex(value: str | None, fallback: str) -> str:
    if not value or not HEX_RE.fullmatch(value):
        return fallback
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    return f"#{value.lower()}"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = normalize_hex(value, "#000000")[1:]
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix(color: str, target: str, amount: float) -> str:
    a, b = hex_to_rgb(color), hex_to_rgb(target)
    amount = min(1, max(0, amount))
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def readable_text(background: str) -> str:
    r, g, b = hex_to_rgb(background)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return "#10131a" if luminance > 0.55 else "#f4f7ff"

