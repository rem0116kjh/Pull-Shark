# git-stats-card

[English](README.md) | [한국어](readme_ko.md)

Fast, serverless-friendly GitHub profile cards rendered as native SVG. No browser,
canvas, or heavyweight rendering runtime required.

```md
![GitHub stats](https://your-deployment.vercel.app/api/card?username=octocat&theme=3d-card)
```

## Themes

| Theme | Character |
| --- | --- |
| `3d-card` | Gradient surface, depth layer, floating animation |
| `cyberpunk` | Neon glow, grid, scanlines, glitch typography |
| `retro-pixel` | Crisp 8-bit borders, arcade colors, blocky bars |
| `minimal-dark` | Restrained glass surface and soft accent lighting |
| `terminal` | Window chrome, monospace body, blinking prompt caret |

Try a theme:

```text
/api/card?username=octocat&theme=cyberpunk
/api/card?username=octocat&theme=retro-pixel&animation=false
/api/card?username=octocat&theme=minimal-dark&show_langs=false
/api/card?username=octocat&theme=terminal
/api/card?username=octocat&bg_color=101828&text_color=f8fafc&border_radius=8
```

## API

`GET /api/card` (alias: `/api/badge`)

| Parameter | Required | Default | Values |
| --- | --- | --- | --- |
| `username` | yes | — | Valid GitHub login |
| `theme` | no | `3d-card` | `3d-card`, `cyberpunk`, `retro-pixel`, `minimal-dark`, `terminal` |
| `show_langs` | no | `true` | Boolean |
| `border_radius` | no | `14` | Integer, 0–20 |
| `bg_color` | no | theme | 3- or 6-digit hex, with or without `#` |
| `text_color` | no | theme | 3- or 6-digit hex, with or without `#` |
| `animation` | no | `true` | Boolean |

Cards return `image/svg+xml` with a four-hour CDN cache and a one-day
stale-while-revalidate window. `GET /health` returns service health.

## GitHub data

One optimized GraphQL request retrieves profile details, annual commits, pull
requests, issues, contributed repository count, repository stars, and language
byte counts. Accounts with more than 100 owned, non-fork repositories use
follow-up repository pages so star and language totals remain complete. GitHub's
GraphQL API does not expose a lifetime commit total; the displayed commit count
covers the rolling past year.

When `GITHUB_TOKEN` is absent—or the upstream request fails and `MOCK_FALLBACK`
is enabled—the service returns deterministic preview data and adds
`X-Git-Stats-Source: fallback`. A nonexistent GitHub user still returns a 404 card.

## Local development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn api.index:app --reload
```

Open `http://localhost:8000/api/card?username=octocat`.

Run tests:

```bash
pytest
```

## Deploy to Vercel

1. Import the repository in Vercel.
2. Add `GITHUB_TOKEN` as an encrypted environment variable.
3. Deploy. The included `vercel.json` routes requests to the FastAPI entrypoint.

The token needs no repository permissions for public profile data. Never put it
in a card URL or commit it to source control.

## Architecture

```text
api/index.py              FastAPI routes and response policy
src/github_client.py      GraphQL request, parsing, fallbacks
src/cache.py              Async TTL cache and request coalescing
src/renderers/            Pure SVG theme renderers
src/utils/                Escaping, formatting, color helpers
tests/                    API, parser, and renderer tests
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, the checks to run before
opening a pull request, and the steps for adding a theme.

## License

MIT
