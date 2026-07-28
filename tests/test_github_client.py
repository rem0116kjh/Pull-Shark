import json

import httpx
import pytest

from src.config import Settings
from src.github_client import GitHubClient


def test_parse_user_aggregates_stars_and_languages():
    user = {
        "login": "octocat",
        "name": "The Octocat",
        "avatarUrl": "https://example.test/avatar.png",
        "bio": "Hello",
        "followers": {"totalCount": 12},
        "pullRequests": {"totalCount": 5},
        "issues": {"totalCount": 3},
        "repositoriesContributedTo": {"totalCount": 9},
        "contributionsCollection": {"totalCommitContributions": 42},
        "repositories": {
            "nodes": [
                {
                    "stargazerCount": 10,
                    "languages": {
                        "edges": [
                            {"size": 80, "node": {"name": "Python", "color": "#3572a5"}},
                            {"size": 20, "node": {"name": "HTML", "color": "#e34c26"}},
                        ]
                    },
                },
                {
                    "stargazerCount": 15,
                    "languages": {
                        "edges": [
                            {"size": 100, "node": {"name": "Python", "color": "#3572a5"}}
                        ]
                    },
                },
            ]
        },
    }
    stats = GitHubClient.parse_user(user)
    assert stats.stars == 25
    assert stats.total_commits == 42
    assert stats.languages[0].name == "Python"
    assert stats.languages[0].percentage == 90.0


def test_parse_user_ignores_nullable_graphql_nodes():
    user = {
        "login": "octocat",
        "repositories": {
            "nodes": [
                None,
                {
                    "stargazerCount": 2,
                    "languages": {
                        "edges": [None, {"size": 10, "node": {"name": "X", "color": "invalid"}}]
                    },
                },
            ]
        },
    }

    stats = GitHubClient.parse_user(user)

    assert stats.stars == 2
    assert stats.languages[0].color == "#8b949e"


@pytest.mark.asyncio
async def test_fetch_user_stats_paginates_repositories():
    requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        body = json.loads(request.content)
        if body["query"].lstrip().startswith("query UserCard"):
            return httpx.Response(
                200,
                json={
                    "data": {
                        "user": {
                            "login": "octocat",
                            "name": "Octocat",
                            "avatarUrl": "",
                            "bio": "",
                            "followers": {"totalCount": 1},
                            "pullRequests": {"totalCount": 2},
                            "issues": {"totalCount": 3},
                            "repositoriesContributedTo": {"totalCount": 4},
                            "contributionsCollection": {"totalCommitContributions": 5},
                            "repositories": {
                                "pageInfo": {"hasNextPage": True, "endCursor": "next"},
                                "nodes": [{"stargazerCount": 10, "languages": {"edges": []}}],
                            },
                        }
                    }
                },
            )
        assert body["variables"]["after"] == "next"
        return httpx.Response(
            200,
            json={
                "data": {
                    "user": {
                        "repositories": {
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": [{"stargazerCount": 20, "languages": {"edges": []}}],
                        }
                    }
                }
            },
        )

    client = GitHubClient(
        Settings(github_token="test-token", mock_fallback=False),
        transport=httpx.MockTransport(handler),
    )
    stats = await client.fetch_user_stats("octocat")

    assert requests == 2
    assert stats.stars == 30
