"""Tests for the company crawler."""

from __future__ import annotations

import json

import pytest
import requests as req
from bs4 import BeautifulSoup

from cvagent.company import _discover_subpages, _fetch_subpage_text, crawl_company

_MAIN_HTML = """
<html>
<head><title>Acme Corp</title></head>
<body>
<nav>Nav</nav>
<main>
<h1>Acme Corp</h1>
<p>We build developer tools that help teams ship faster.</p>
<a href="/about">About us</a>
<a href="/products">Products</a>
<a href="https://external.com/other">External</a>
<a href="/blog">Blog</a>
</main>
<footer>Footer</footer>
</body>
</html>
"""

_ABOUT_HTML = """
<html><body>
<main>
<h2>About Acme</h2>
<p>Founded in 2018, Acme uses Python and Kubernetes to power its platform.</p>
</main>
</body></html>
"""

_COMPANY_INFO = {
    "name": "Acme Corp",
    "industry": "Developer Tools / SaaS",
    "mission": "Help teams ship faster with great tooling.",
    "products": "CI/CD pipeline, code review automation",
    "tech_signals": "Python, Kubernetes, React",
    "culture": "Remote-first, fast-moving startup",
}


def test_crawl_company_success(mocker):
    def fake_get(url, **kwargs):
        mock = mocker.MagicMock()
        mock.raise_for_status = mocker.MagicMock()
        mock.text = _ABOUT_HTML if "about" in url else _MAIN_HTML
        return mock

    mocker.patch("cvagent.company.requests.get", side_effect=fake_get)
    mocker.patch("cvagent.llm.generate", return_value=json.dumps(_COMPANY_INFO))

    result = crawl_company("https://acme.com", model="mistral", provider="ollama")

    assert result["name"] == "Acme Corp"
    assert result["url"] == "https://acme.com"
    for key in ("name", "industry", "mission", "products", "tech_signals", "culture"):
        assert key in result


def test_crawl_company_returns_url_key(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_resp.text = _MAIN_HTML
    mocker.patch("cvagent.company.requests.get", return_value=mock_resp)
    mocker.patch("cvagent.llm.generate", return_value=json.dumps(_COMPANY_INFO))

    result = crawl_company("https://acme.com")
    assert result["url"] == "https://acme.com"


def test_crawl_company_main_page_http_error(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status.side_effect = req.HTTPError("403")
    mocker.patch("cvagent.company.requests.get", return_value=mock_resp)

    with pytest.raises(req.HTTPError):
        crawl_company("https://acme.com")


def test_subpage_network_error_ignored(mocker):
    call_count = {"n": 0}

    def fake_get(url, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            mock = mocker.MagicMock()
            mock.raise_for_status = mocker.MagicMock()
            mock.text = _MAIN_HTML
            return mock
        raise req.ConnectionError("timeout")

    mocker.patch("cvagent.company.requests.get", side_effect=fake_get)
    mocker.patch("cvagent.llm.generate", return_value=json.dumps(_COMPANY_INFO))

    result = crawl_company("https://acme.com")
    assert result["name"] == "Acme Corp"


def test_discover_subpages_filters_correctly():
    soup = BeautifulSoup(_MAIN_HTML, "html.parser")
    urls = _discover_subpages(soup, base_url="https://acme.com")

    assert any("about" in u for u in urls)
    assert any("product" in u for u in urls)
    assert not any("external.com" in u for u in urls)
    assert not any("blog" in u for u in urls)


def test_discover_subpages_max_pages():
    html = """
    <html><body>
    <a href="/about">About</a>
    <a href="/team">Team</a>
    <a href="/products">Products</a>
    <a href="/mission">Mission</a>
    <a href="/culture">Culture</a>
    <a href="/values">Values</a>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    urls = _discover_subpages(soup, base_url="https://acme.com", max_pages=3)
    assert len(urls) <= 3


def test_fetch_subpage_text_returns_empty_on_error(mocker):
    mocker.patch("cvagent.company.requests.get", side_effect=req.ConnectionError("down"))
    result = _fetch_subpage_text("https://acme.com/about")
    assert result == ""


def test_crawl_company_fills_missing_llm_keys(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status = mocker.MagicMock()
    mock_resp.text = _MAIN_HTML
    mocker.patch("cvagent.company.requests.get", return_value=mock_resp)
    # LLM returns partial data — missing tech_signals and culture
    partial = {"name": "Acme Corp", "industry": "SaaS", "mission": "Ship faster", "products": "CI tool"}
    mocker.patch("cvagent.llm.generate", return_value=json.dumps(partial))

    result = crawl_company("https://acme.com")
    assert result["tech_signals"] == "Unknown"
    assert result["culture"] == "Unknown"
