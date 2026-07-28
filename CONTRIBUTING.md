# Contributing

Thanks for taking the time to contribute.

## Local setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn api.index:app --reload
```

Open `http://localhost:8000/api/card?username=octocat` to see a card.

`GITHUB_TOKEN` is optional for local work. Without it the service returns
deterministic mock data and sets `X-Git-Stats-Source: fallback`.

## Before opening a pull request

```bash
ruff check .
pytest -q
```

Both must pass. Lint rules live in `pyproject.toml`.

## Commit messages

Conventional Commits, one logical change per commit:

```
<type>: <description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.

## Adding a theme

Themes are pure SVG string builders — no browser, no canvas, no headless
runtime. To add one:

1. Create `src/renderers/<name>.py` with a class extending `BaseRenderer`.
2. Implement `render(self, stats: UserStats, options: RenderOptions) -> str`.
   Reuse `identity()`, `stats_grid()`, `languages()`, and `base_style()` from
   the base class so layout stays consistent across themes.
3. Register the theme in `RENDERERS` in `src/renderers/__init__.py`.
4. Add the theme name to the `theme` query pattern in `api/index.py`.
5. Document it in the theme table in both `README.md` and `readme_ko.md`.

`tests/test_renderers.py` parametrizes over `RENDERERS`, so a registered theme
is covered by the shared safety tests automatically.

## Rules for renderer code

- Escape every value that comes from the GitHub API with `xml_escape`.
- Honor `options.animation`; wrap all motion so it can be turned off.
- Keep `@media (prefers-reduced-motion: reduce)` support intact.
- Never emit `<script>` into a card.

## Reporting bugs

Include the full card URL that reproduces the problem, the expected result, and
the actual result. Never paste a `GITHUB_TOKEN` into an issue.
