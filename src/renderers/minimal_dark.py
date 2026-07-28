from src.models import UserStats
from src.renderers.base import BaseRenderer, RenderOptions
from src.utils.color import mix
from src.utils.svg_helpers import xml_escape


class MinimalDarkRenderer(BaseRenderer):
    def render(self, stats: UserStats, options: RenderOptions) -> str:
        width, height = self.dimensions(options)
        bg, text = self.colors(options, "#0b0d12", "#f0f2f5")
        accent = "#a3e635"
        animation = (
            "@keyframes breathe{50%{opacity:.65}}.orb{animation:breathe 4s ease-in-out infinite}"
            if options.animation
            else ""
        )
        langs = (
            self.languages(stats, text, mix(bg, "#ffffff", 0.1), width) if options.show_langs else ""
        )
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
          viewBox="0 0 {width} {height}" role="img" aria-label="GitHub stats for {xml_escape(stats.username)}">
          <defs>
            <radialGradient id="orb"><stop stop-color="#a3e635" stop-opacity=".22"/><stop offset="1" stop-opacity="0"/></radialGradient>
            <linearGradient id="glass" x2="1" y2="1"><stop stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity=".015"/></linearGradient>
            <clipPath id="avatarClip"><circle cx="79" cy="82" r="36"/></clipPath>
            {self.base_style()}<style>{animation}</style>
          </defs>
          <rect width="{width}" height="{height}" rx="{options.border_radius}" fill="{bg}"/>
          <circle class="orb" cx="{width - 70}" cy="20" r="190" fill="url(#orb)"/>
          <rect x=".75" y=".75" width="{width - 1.5}" height="{height - 1.5}" rx="{options.border_radius}"
            fill="url(#glass)" stroke="#fff" stroke-opacity=".12" stroke-width="1.5"/>
          {self.identity(stats, text, accent)}
          <path d="M42 148H{width - 42}" stroke="#fff" stroke-opacity=".08"/>
          {self.stats_grid(stats, text, accent, width)}
          {langs}
          <text x="{width - 42}" y="{height - 24}" text-anchor="end" class="label" fill="{text}" opacity=".25">GITHUB PROFILE</text>
        </svg>"""
