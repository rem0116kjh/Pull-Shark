import re

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from src.cache import AsyncTTLCache
from src.config import get_settings
from src.github_client import GitHubAPIError, GitHubClient, RateLimitError, UserNotFoundError
from src.models import UserStats
from src.renderers import RENDERERS, RenderOptions

settings = get_settings()
client = GitHubClient(settings)
cache: AsyncTTLCache[UserStats] = AsyncTTLCache(
    settings.cache_ttl_seconds, settings.stale_ttl_seconds
)
app = FastAPI(
    title="git-stats-card",
    description="Dynamic 3D and pixel GitHub statistics SVG cards.",
    version="1.0.0",
    docs_url="/docs",
)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
CACHE_CONTROL = (
    f"public, max-age={settings.cache_ttl_seconds}, "
    f"s-maxage={settings.cache_ttl_seconds}, "
    f"stale-while-revalidate={settings.stale_ttl_seconds}"
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "git-stats-card"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "git-stats-card", "card": "/api/card?username=octocat", "docs": "/docs"}


@app.get("/api/card", response_class=Response)
@app.get("/api/badge", response_class=Response, include_in_schema=False)
async def card(
    username: str = Query(..., min_length=1, max_length=39),
    theme: str = Query("3d-card", pattern="^(3d-card|cyberpunk|retro-pixel|minimal-dark)$"),
    show_langs: bool = True,
    border_radius: int = Query(14, ge=0, le=20),
    bg_color: str | None = Query(None, pattern="^#?[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$"),
    text_color: str | None = Query(None, pattern="^#?[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$"),
    animation: bool = True,
) -> Response:
    username = username.strip()
    if not USERNAME_RE.fullmatch(username):
        return error_svg("Invalid GitHub username", 422)

    try:
        stats = await cache.get_or_set(
            username.lower(), lambda: client.fetch_user_stats(username)
        )
        options = RenderOptions(
            show_langs=show_langs,
            border_radius=border_radius,
            bg_color=bg_color,
            text_color=text_color,
            animation=animation,
        )
        svg = RENDERERS[theme].render(stats, options)
        headers = {
            "Cache-Control": CACHE_CONTROL,
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; img-src https: data:; style-src 'unsafe-inline'",
            "Vary": "Accept-Encoding",
        }
        if stats.is_mock:
            headers["X-Git-Stats-Source"] = "fallback"
        return Response(svg, media_type="image/svg+xml", headers=headers)
    except UserNotFoundError as exc:
        return error_svg(str(exc), 404)
    except RateLimitError:
        return error_svg("GitHub API rate limit exceeded", 429)
    except GitHubAPIError:
        return error_svg("Unable to fetch GitHub statistics", 502)


def error_svg(message: str, status_code: int) -> Response:
    from src.utils.svg_helpers import xml_escape

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="520" height="100" role="img">
      <rect width="520" height="100" rx="12" fill="#111827"/>
      <circle cx="45" cy="50" r="20" fill="#ef4444"/>
      <text x="45" y="57" text-anchor="middle" fill="white" font-size="22" font-family="sans-serif">!</text>
      <text x="80" y="56" fill="#f8fafc" font-size="16" font-family="sans-serif">{xml_escape(message)}</text>
    </svg>"""
    return Response(
        svg,
        status_code=status_code,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.exception_handler(Exception)
async def unhandled_error(request: Request, __: Exception) -> JSONResponse | Response:
    if request.url.path in {"/api/card", "/api/badge"}:
        return error_svg("Internal server error", 500)
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse | Response:
    if request.url.path in {"/api/card", "/api/badge"}:
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(part) for part in first.get("loc", ())[1:])
        message = f"Invalid {field or 'request parameter'}"
        return error_svg(message, 422)
    return JSONResponse({"detail": exc.errors()}, status_code=422)
