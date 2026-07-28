from src.models import UserStats
from src.renderers.base import BaseRenderer, RenderOptions
from src.utils.svg_helpers import xml_escape


class RetroPixelRenderer(BaseRenderer):
    def render(self, stats: UserStats, options: RenderOptions) -> str:
        width, height = self.dimensions(options)
        bg, text = self.colors(options, "#211a38", "#fff4d2")
        accent = "#ffcc33"
        animation = (
            "@keyframes blink{50%{opacity:.35}}.cursor{animation:blink 1s steps(1) infinite}"
            if options.animation
            else ""
        )
        langs = self.languages(stats, text, "#463b68", width) if options.show_langs else ""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
          viewBox="0 0 {width} {height}" shape-rendering="crispEdges" role="img"
          aria-label="GitHub stats for {xml_escape(stats.username)}">
          <defs>
            <clipPath id="avatarClip"><circle cx="79" cy="82" r="36"/></clipPath>
            {self.base_style("ui-monospace,Menlo,Consolas,monospace")}
            <style>{animation}.name,.value{{font-weight:900}} text{{shape-rendering:auto}}</style>
          </defs>
          <rect width="{width}" height="{height}" fill="{bg}"/>
          <path d="M8 8H{width - 8}V{height - 8}H8z" fill="none" stroke="#ff4d9d" stroke-width="8"/>
          <path d="M16 16H{width - 16}V{height - 16}H16z" fill="none" stroke="{accent}" stroke-width="4"/>
          <g opacity=".16" fill="#fff">
            <rect x="28" y="28" width="8" height="8"/>
            <rect x="{width - 40}" y="44" width="8" height="8"/>
            <rect x="{width - 60}" y="{height - 48}" width="8" height="8"/>
          </g>
          {self.identity(stats, text, accent)}
          {self.stats_grid(stats, text, "#65f4a5", width)}
          {langs}
          <rect class="cursor" x="42" y="{height - 29}" width="9" height="12" fill="#65f4a5"/>
          <text x="59" y="{height - 19}" class="label" fill="#65f4a5">READY.</text>
        </svg>"""
