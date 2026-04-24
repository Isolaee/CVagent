"""Crawl a company website and extract structured company information."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

_SUBPAGE_KEYWORDS = {"about", "team", "product", "mission", "value", "culture", "story", "career", "us"}

_COMPANY_INFO_KEYS = {"name", "industry", "mission", "products", "tech_signals", "culture"}


def crawl_company(url: str, model: str = "mistral", provider: str = "ollama") -> dict[str, Any]:
    """Crawl a company website and return structured company info.

    Fetches the main page and up to 4 relevant subpages, then uses the LLM to
    extract a structured company profile for use in open application prompts.

    Raises requests.HTTPError if the main page cannot be fetched.
    Raises ValueError if the LLM response cannot be parsed.
    """
    print(f"Fetching main page: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; CVAgent/1.0)"}, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    main_text = _page_text_from_soup(soup, char_limit=3000)

    subpage_urls = _discover_subpages(soup, base_url=url)
    texts = [main_text]
    for sub_url in subpage_urls:
        print(f"Fetching subpage: {sub_url}")
        sub_text = _fetch_subpage_text(sub_url)
        if sub_text:
            texts.append(sub_text)

    combined = "\n\n".join(texts)[:12000]
    print("Extracting company profile with LLM...")
    info = _extract_company_info(combined, model=model, provider=provider)
    info["url"] = url
    return info


def _discover_subpages(soup: BeautifulSoup, base_url: str, max_pages: int = 4) -> list[str]:
    """Return same-domain subpage URLs whose path matches known company page keywords."""
    base_domain = urlparse(base_url).netloc
    seen: set[str] = set()
    results: list[str] = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        if parsed.netloc != base_domain:
            continue
        if absolute in seen or absolute == base_url:
            continue

        path_lower = parsed.path.lower().replace("-", "").replace("_", "")
        if any(kw in path_lower for kw in _SUBPAGE_KEYWORDS):
            seen.add(absolute)
            results.append(absolute)
            if len(results) >= max_pages:
                break

    return results


def _fetch_subpage_text(url: str, char_limit: int = 3000) -> str:
    """Fetch a subpage and return its text; returns empty string on any error."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CVAgent/1.0)"},
            timeout=10,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return _page_text_from_soup(soup, char_limit=char_limit)
    except requests.RequestException:
        return ""


def _page_text_from_soup(soup: BeautifulSoup, char_limit: int = 3000) -> str:
    """Strip non-content tags and return collapsed plain text, capped at char_limit."""
    for tag in soup(["script", "style", "nav", "footer", "header", "meta"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:char_limit]


def _extract_company_info(combined_text: str, model: str, provider: str) -> dict[str, Any]:
    """Use the LLM to extract structured company info from crawled page text."""
    from cvagent.llm import generate

    prompt = (
        "You are a company profile extractor. Read the web content below and return ONLY a valid JSON object "
        "with these keys:\n"
        '  "name"         – company name (string)\n'
        '  "industry"     – industry or sector (string)\n'
        '  "mission"      – company mission or value proposition in 1–2 sentences (string)\n'
        '  "products"     – main products or services, comma-separated (string)\n'
        '  "tech_signals" – technologies, platforms, or languages visible in the content (string, or "Unknown")\n'
        '  "culture"      – culture descriptors such as remote-first, startup, enterprise (string)\n\n'
        "Return only the JSON object, no explanation, no markdown fences.\n\n"
        f"Web content:\n{combined_text}"
    )

    raw = generate(prompt, model=model, provider=provider)
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw.strip())

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned non-JSON response. Raw output:\n{raw}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got: {type(data).__name__}")

    missing = _COMPANY_INFO_KEYS - set(data.keys())
    for key in missing:
        data[key] = "Unknown"

    return data
