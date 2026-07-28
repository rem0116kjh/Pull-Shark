from src.renderers.base import (
    DEFAULT_CARD_WIDTH,
    MAX_CARD_WIDTH,
    MIN_CARD_WIDTH,
    RenderOptions,
)
from src.renderers.card_3d import Card3DRenderer
from src.renderers.cyberpunk import CyberpunkRenderer
from src.renderers.minimal_dark import MinimalDarkRenderer
from src.renderers.retro_pixel import RetroPixelRenderer
from src.renderers.terminal import TerminalRenderer

RENDERERS = {
    "3d-card": Card3DRenderer(),
    "cyberpunk": CyberpunkRenderer(),
    "retro-pixel": RetroPixelRenderer(),
    "minimal-dark": MinimalDarkRenderer(),
    "terminal": TerminalRenderer(),
}

__all__ = [
    "DEFAULT_CARD_WIDTH",
    "MAX_CARD_WIDTH",
    "MIN_CARD_WIDTH",
    "RENDERERS",
    "RenderOptions",
]

