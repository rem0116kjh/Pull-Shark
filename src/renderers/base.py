from dataclasses import dataclass

from src.models import UserStats
from src.utils.color import normalize_hex
from src.utils.svg_helpers import format_number, truncate, xml_escape


@dataclass(frozen=True, slots=True)
class RenderOptions:
    show_langs: bool = True
    border_radius: int = 14
    bg_color: str | None = None
    text_color: str | None = None
    animation: bool = True


class BaseRenderer:
    width = 760

    def colors(
        self, options: RenderOptions, default_bg: str, default_text: str
    ) -> tuple[str, str]:
        return (
            normalize_hex(options.bg_color, default_bg),
            normalize_hex(options.text_color, default_text),
        )

    def dimensions(self, options: RenderOptions) -> tuple[int, int]:
        return self.width, 410 if options.show_langs else 315

    def identity(self, stats: UserStats, text: str, accent: str) -> str:
        initial = xml_escape((stats.name or stats.username or "?")[0].upper())
        return f"""
        <circle cx="79" cy="82" r="36" fill="{accent}" opacity=".18"/>
        <text x="79" y="94" text-anchor="middle" class="avatar-fallback" fill="{accent}">{initial}</text>
        <image href="{xml_escape(stats.avatar_url)}" x="42" y="45" width="74" height="74"
          clip-path="url(#avatarClip)" preserveAspectRatio="xMidYMid slice"/>
        <circle cx="79" cy="82" r="39" fill="none" stroke="{accent}" stroke-width="3"/>
        <text x="140" y="72" class="name" fill="{text}">{xml_escape(truncate(stats.name, 30))}</text>
        <text x="140" y="100" class="handle" fill="{accent}">@{xml_escape(stats.username)}</text>
        <text x="140" y="126" class="bio" fill="{text}" opacity=".68">{xml_escape(truncate(stats.bio, 66))}</text>
        """

    def stats_grid(self, stats: UserStats, text: str, accent: str) -> str:
        values = [
            ("COMMITS", stats.total_commits),
            ("PULL REQUESTS", stats.pull_requests),
            ("ISSUES", stats.issues),
            ("STARS", stats.stars),
            ("REPOS", stats.contributed_repos),
            ("FOLLOWERS", stats.followers),
        ]
        cells = []
        for index, (label, value) in enumerate(values):
            x = 42 + (index % 3) * 232
            y = 175 + (index // 3) * 70
            cells.append(
                f'<text x="{x}" y="{y}" class="value" fill="{text}">{format_number(value)}</text>'
                f'<text x="{x}" y="{y + 23}" class="label" fill="{accent}">{label}</text>'
            )
        return "".join(cells)

    def languages(self, stats: UserStats, text: str, bar_bg: str) -> str:
        if not stats.languages:
            return ""
        x, width = 42, 676
        segments, labels, cursor = [], [], x
        for index, lang in enumerate(stats.languages):
            segment_width = width * lang.percentage / 100
            segments.append(
                f'<rect x="{cursor:.1f}" y="326" width="{segment_width + .5:.1f}" '
                f'height="10" fill="{lang.color or "#8b949e"}"/>'
            )
            if index < 4:
                label_x = x + index * 169
                labels.append(
                    f'<circle cx="{label_x + 5}" cy="363" r="5" fill="{lang.color or "#8b949e"}"/>'
                    f'<text x="{label_x + 17}" y="368" class="lang" fill="{text}">'
                    f'{xml_escape(truncate(lang.name, 12))} {lang.percentage:.1f}%</text>'
                )
            cursor += segment_width
        return (
            f'<text x="42" y="310" class="section" fill="{text}">PRIMARY LANGUAGES</text>'
            f'<rect x="{x}" y="326" width="{width}" height="10" rx="5" fill="{bar_bg}"/>'
            + "".join(segments)
            + "".join(labels)
        )

    def base_style(self, font: str = "system-ui,-apple-system,Segoe UI,sans-serif") -> str:
        return f"""
        <style>
          text {{ font-family:{font}; }}
          .name {{ font-size:25px;font-weight:750 }}
          .handle {{ font-size:14px;font-weight:650 }}
          .bio {{ font-size:13px }}
          .avatar-fallback {{ font-size:34px;font-weight:800 }}
          .value {{ font-size:25px;font-weight:750 }}
          .label {{ font-size:10px;font-weight:750;letter-spacing:1.3px }}
          .section {{ font-size:11px;font-weight:750;letter-spacing:1.4px }}
          .lang {{ font-size:11px;font-weight:600 }}
          @media (prefers-reduced-motion: reduce) {{
            * {{ animation:none!important }}
          }}
        </style>
        """

    def render(self, stats: UserStats, options: RenderOptions) -> str:
        raise NotImplementedError
