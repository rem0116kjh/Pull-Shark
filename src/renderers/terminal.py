from src.models import UserStats
from src.renderers.base import BaseRenderer, RenderOptions
from src.utils.color import mix
from src.utils.svg_helpers import truncate, xml_escape

TITLE_BAR_HEIGHT = 34


class TerminalRenderer(BaseRenderer):
    """A terminal window: title bar, monospace body, blinking prompt caret."""

    def render(self, stats: UserStats, options: RenderOptions) -> str:
        width, height = self.dimensions(options)
        bg, text = self.colors(options, "#0d1117", "#c9d1d9")
        accent = "#3fb950"
        bar = mix(bg, "#ffffff", 0.08)
        animation = (
            "@keyframes caret{50%{opacity:0}}.caret{animation:caret 1.1s steps(1) infinite}"
            if options.animation
            else ""
        )
        langs = self.languages(stats, text, mix(bg, "#ffffff", 0.12)) if options.show_langs else ""
        title = xml_escape(f"{truncate(stats.username, 24)}@github: ~/stats")
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
          viewBox="0 0 {width} {height}" role="img"
          aria-label="GitHub stats for {xml_escape(stats.username)}">
          <defs>
            <clipPath id="cardClip">
              <rect width="{width}" height="{height}" rx="{options.border_radius}"/>
            </clipPath>
            <clipPath id="avatarClip"><circle cx="79" cy="82" r="36"/></clipPath>
            {self.base_style("ui-monospace,SFMono-Regular,Menlo,Consolas,monospace")}
            <style>{animation}.title{{font-size:12px;font-weight:650;letter-spacing:.4px}}
              .prompt{{font-size:12px;font-weight:650}}</style>
          </defs>
          <g clip-path="url(#cardClip)">
            <rect width="{width}" height="{height}" fill="{bg}"/>
            <rect width="{width}" height="{TITLE_BAR_HEIGHT}" fill="{bar}"/>
            <circle cx="24" cy="17" r="5.5" fill="#ff5f56"/>
            <circle cx="43" cy="17" r="5.5" fill="#ffbd2e"/>
            <circle cx="62" cy="17" r="5.5" fill="#27c93f"/>
            <text x="{width / 2}" y="21" text-anchor="middle" class="title" fill="{text}"
              opacity=".62">{title}</text>
          </g>
          <path d="M0 {TITLE_BAR_HEIGHT}H{width}" stroke="#fff" stroke-opacity=".1"/>
          {self.identity(stats, text, accent)}
          <path d="M42 148H718" stroke="#fff" stroke-opacity=".08"/>
          {self.stats_grid(stats, text, accent)}
          {langs}
          <text x="42" y="{height - 20}" class="prompt" fill="{accent}">$ gh stats --user {xml_escape(truncate(stats.username, 20))}</text>
          <rect class="caret" x="220" y="{height - 31}" width="8" height="14"
            fill="{accent}" opacity=".85"/>
          <rect x=".75" y=".75" width="{width - 1.5}" height="{height - 1.5}"
            rx="{options.border_radius}" fill="none" stroke="#fff" stroke-opacity=".1"
            stroke-width="1.5"/>
        </svg>"""
