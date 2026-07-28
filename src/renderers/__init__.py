from src.renderers.base import RenderOptions
from src.renderers.card_3d import Card3DRenderer
from src.renderers.cyberpunk import CyberpunkRenderer
from src.renderers.minimal_dark import MinimalDarkRenderer
from src.renderers.retro_pixel import RetroPixelRenderer

RENDERERS = {
    "3d-card": Card3DRenderer(),
    "cyberpunk": CyberpunkRenderer(),
    "retro-pixel": RetroPixelRenderer(),
    "minimal-dark": MinimalDarkRenderer(),
}

__all__ = ["RENDERERS", "RenderOptions"]

