from src.models import UserStats
from src.renderers.base import BaseRenderer, RenderOptions
from src.utils.svg_helpers import xml_escape


class CyberpunkRenderer(BaseRenderer):
    def render(self, stats: UserStats, options: RenderOptions) -> str:
        width, height = self.dimensions(options)
        bg, text = self.colors(options, "#050816", "#e8fbff")
        accent = "#00f6ff"
        animation = (
            "@keyframes pulse{50%{filter:drop-shadow(0 0 8px #ff2bd6)}}"
            ".frame{animation:pulse 2.8s steps(2) infinite}"
            if options.animation
            else ""
        )
        langs = self.languages(stats, text, "#18203b") if options.show_langs else ""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
          viewBox="0 0 {width} {height}" role="img" aria-label="GitHub stats for {xml_escape(stats.username)}">
          <defs>
            <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M24 0H0V24" fill="none" stroke="#00f6ff" stroke-opacity=".09"/>
            </pattern>
            <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
              <path d="M0 3.5H4" stroke="#fff" stroke-opacity=".025"/>
            </pattern>
            <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            <clipPath id="avatarClip"><circle cx="79" cy="82" r="36"/></clipPath>
            {self.base_style("ui-monospace,SFMono-Regular,Consolas,monospace")}
            <style>{animation}.name{{text-shadow:2px 0 #ff2bd6,-2px 0 #00f6ff}}</style>
          </defs>
          <rect width="{width}" height="{height}" rx="{options.border_radius}" fill="{bg}"/>
          <rect width="{width}" height="{height}" rx="{options.border_radius}" fill="url(#grid)"/>
          <g class="frame">
            <path d="M20 2H700l58 58v{height - 80}l-20 20H2V20z" fill="none"
              stroke="{accent}" stroke-width="2" filter="url(#glow)"/>
            <path d="M2 140h20l12 12h692l12-12h20" stroke="#ff2bd6" fill="none" opacity=".8"/>
          </g>
          {self.identity(stats, text, accent)}
          {self.stats_grid(stats, text, "#ff2bd6")}
          {langs}
          <rect width="{width}" height="{height}" rx="{options.border_radius}" fill="url(#scan)" pointer-events="none"/>
          <text x="718" y="{height - 22}" text-anchor="end" class="label" fill="{accent}">SYS::GITHUB//STATS</text>
        </svg>"""
