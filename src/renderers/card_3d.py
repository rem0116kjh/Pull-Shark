from src.models import UserStats
from src.renderers.base import BaseRenderer, RenderOptions
from src.utils.color import mix
from src.utils.svg_helpers import xml_escape


class Card3DRenderer(BaseRenderer):
    def render(self, stats: UserStats, options: RenderOptions) -> str:
        width, height = self.dimensions(options)
        bg, text = self.colors(options, "#111827", "#f8fafc")
        accent, edge = "#7c5cff", mix(bg, "#000000", 0.45)
        animate = (
            "@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}"
            ".card{animation:float 5s ease-in-out infinite;transform-origin:center}"
            if options.animation
            else ""
        )
        langs = self.languages(stats, text, mix(bg, "#ffffff", 0.12)) if options.show_langs else ""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
          viewBox="0 0 {width} {height}" role="img" aria-label="GitHub stats for {xml_escape(stats.username)}">
          <defs>
            <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="{mix(bg, "#ffffff", .08)}"/><stop offset="1" stop-color="{bg}"/>
            </linearGradient>
            <linearGradient id="shine"><stop stop-color="{accent}"/><stop offset="1" stop-color="#2dd4bf"/></linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="160%" height="170%">
              <feDropShadow dx="0" dy="13" stdDeviation="14" flood-color="#000" flood-opacity=".42"/>
            </filter>
            <clipPath id="avatarClip"><circle cx="79" cy="82" r="36"/></clipPath>
            {self.base_style()}<style>{animate}</style>
          </defs>
          <g class="card">
            <path d="M28 22h688q20 0 20 20v{height - 57}q0 20-20 20H28z" fill="{edge}" opacity=".8"/>
            <rect x="18" y="12" width="718" height="{height - 34}" rx="{options.border_radius}"
              fill="url(#surface)" stroke="url(#shine)" stroke-width="1.5" filter="url(#shadow)"/>
            <path d="M{18 + options.border_radius} 13h{718 - options.border_radius * 2}"
              stroke="white" opacity=".12"/>
            {self.identity(stats, text, accent)}
            {self.stats_grid(stats, text, accent)}
            {langs}
            <text x="718" y="{height - 25}" text-anchor="end" class="label" fill="{text}" opacity=".28">GIT-STATS-CARD</text>
          </g>
        </svg>"""
