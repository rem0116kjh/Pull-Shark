from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class LanguageStat:
    name: str
    color: str
    size: int
    percentage: float = 0


@dataclass(frozen=True, slots=True)
class UserStats:
    username: str
    name: str
    avatar_url: str
    bio: str
    followers: int
    total_commits: int
    pull_requests: int
    issues: int
    stars: int
    contributed_repos: int
    languages: tuple[LanguageStat, ...] = field(default_factory=tuple)
    is_mock: bool = False

