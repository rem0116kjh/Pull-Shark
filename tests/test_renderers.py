import pytest

from src.github_client import GitHubClient
from src.renderers import RENDERERS, RenderOptions


@pytest.mark.parametrize("theme", RENDERERS)
def test_renderer_produces_safe_svg(theme):
    stats = GitHubClient.mock_stats('octo<script>alert("x")</script>')
    svg = RENDERERS[theme].render(stats, RenderOptions())
    assert svg.startswith("<svg")
    assert "<script>" not in svg
    assert "PRIMARY LANGUAGES" in svg
    assert 'role="img"' in svg


def test_language_section_can_be_hidden():
    svg = RENDERERS["3d-card"].render(
        GitHubClient.mock_stats("octocat"), RenderOptions(show_langs=False)
    )
    assert "PRIMARY LANGUAGES" not in svg
    assert 'height="315"' in svg

