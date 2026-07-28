from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import httpx

from src.config import Settings
from src.models import LanguageStat, UserStats
from src.utils.color import normalize_hex

logger = logging.getLogger(__name__)

QUERY = """
query UserCard($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login name avatarUrl bio followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(
      first: 1
      contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]
      includeUserRepositories: true
    ) { totalCount }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      isFork: false
      orderBy: { field: STARGAZERS, direction: DESC }
    ) {
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name color } }
        }
      }
    }
  }
  rateLimit { remaining resetAt }
}
"""

REPOSITORIES_QUERY = """
query UserRepositories($login: String!, $after: String!) {
  user(login: $login) {
    repositories(
      first: 100
      after: $after
      ownerAffiliations: OWNER
      isFork: false
      orderBy: { field: STARGAZERS, direction: DESC }
    ) {
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name color } }
        }
      }
    }
  }
  rateLimit { remaining resetAt }
}
"""


class GitHubAPIError(RuntimeError):
    pass


class UserNotFoundError(GitHubAPIError):
    pass


class RateLimitError(GitHubAPIError):
    pass


class GitHubClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.transport = transport

    async def fetch_user_stats(self, username: str) -> UserStats:
        if not self.settings.github_token:
            return self.mock_stats(username)

        now = datetime.now(UTC)
        variables = {
            "login": username,
            "from": (now - timedelta(days=365)).isoformat(),
            "to": now.isoformat(),
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.request_timeout_seconds,
                transport=self.transport,
            ) as client:
                payload = await self._post_graphql(client, QUERY, variables)
                user = payload.get("data", {}).get("user")
                if not user:
                    raise UserNotFoundError(f"GitHub user '{username}' was not found")

                repositories = user.get("repositories") or {}
                nodes = list(repositories.get("nodes") or [])
                page_info = repositories.get("pageInfo") or {}
                while page_info.get("hasNextPage"):
                    cursor = page_info.get("endCursor")
                    if not cursor:
                        raise GitHubAPIError("Repository pagination cursor was missing")
                    page_payload = await self._post_graphql(
                        client,
                        REPOSITORIES_QUERY,
                        {"login": username, "after": cursor},
                    )
                    page_user = page_payload.get("data", {}).get("user")
                    if not page_user:
                        raise UserNotFoundError(f"GitHub user '{username}' was not found")
                    page = page_user.get("repositories") or {}
                    nodes.extend(page.get("nodes") or [])
                    page_info = page.get("pageInfo") or {}
                repositories["nodes"] = nodes
                user["repositories"] = repositories

            return self.parse_user(user)
        except UserNotFoundError:
            raise
        except (RateLimitError, httpx.HTTPError, ValueError, GitHubAPIError) as exc:
            if not self.settings.mock_fallback:
                raise
            logger.warning("GitHub request failed for %s; using fallback: %s", username, exc)
            return self.mock_stats(username)

    async def _post_graphql(
        self, client: httpx.AsyncClient, query: str, variables: dict[str, object]
    ) -> dict:
        response = await client.post(
            self.settings.github_api_url,
            json={"query": query, "variables": variables},
            headers={
                "Authorization": f"Bearer {self.settings.github_token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "git-stats-card",
            },
        )
        if response.status_code in (403, 429):
            raise RateLimitError("GitHub API rate limit exceeded")
        response.raise_for_status()
        payload = response.json()
        errors = payload.get("errors") or []
        if errors:
            message = "; ".join(str(error.get("message", "GraphQL error")) for error in errors)
            if "rate limit" in message.lower():
                raise RateLimitError(message)
            raise GitHubAPIError(message)
        return payload

    @staticmethod
    def parse_user(user: dict) -> UserStats:
        repos = [repo for repo in (user.get("repositories", {}).get("nodes") or []) if repo]
        stars = sum(repo.get("stargazerCount") or 0 for repo in repos)
        language_sizes: dict[str, tuple[int, str]] = {}
        for repo in repos:
            for edge in (repo.get("languages") or {}).get("edges") or []:
                if not edge:
                    continue
                node = edge.get("node") or {}
                name = node.get("name")
                if not name:
                    continue
                github_color = normalize_hex(node.get("color"), "#8b949e")
                old_size, old_color = language_sizes.get(name, (0, github_color))
                language_sizes[name] = (old_size + (edge.get("size") or 0), old_color)
        total = sum(size for size, _ in language_sizes.values()) or 1
        languages = tuple(
            LanguageStat(name, color, size, round(size / total * 100, 1))
            for name, (size, color) in sorted(
                language_sizes.items(), key=lambda item: item[1][0], reverse=True
            )[:5]
        )
        return UserStats(
            username=user.get("login") or "",
            name=user.get("name") or user.get("login") or "",
            avatar_url=user.get("avatarUrl") or "",
            bio=user.get("bio") or "",
            followers=(user.get("followers") or {}).get("totalCount") or 0,
            total_commits=(user.get("contributionsCollection") or {}).get(
                "totalCommitContributions", 0
            ),
            pull_requests=(user.get("pullRequests") or {}).get("totalCount") or 0,
            issues=(user.get("issues") or {}).get("totalCount") or 0,
            stars=stars,
            contributed_repos=(user.get("repositoriesContributedTo") or {}).get(
                "totalCount", 0
            ),
            languages=languages,
        )

    @staticmethod
    def mock_stats(username: str) -> UserStats:
        seed = sum(ord(char) for char in username)
        languages = (
            LanguageStat("TypeScript", "#3178c6", 48_000, 41.0),
            LanguageStat("Python", "#3572a5", 34_000, 29.1),
            LanguageStat("Rust", "#dea584", 22_000, 18.8),
            LanguageStat("Other", "#8b949e", 13_000, 11.1),
        )
        return UserStats(
            username=username,
            name=username,
            avatar_url=f"https://github.com/{username}.png",
            bio="GitHub developer • fallback preview",
            followers=120 + seed % 1800,
            total_commits=400 + seed % 2600,
            pull_requests=30 + seed % 380,
            issues=12 + seed % 160,
            stars=80 + seed % 5500,
            contributed_repos=8 + seed % 75,
            languages=languages,
            is_mock=True,
        )
