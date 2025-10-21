from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from readability import Document

from .utils import PAGES_DIR

USER_AGENT = "MyLocalAI/1.0 (+https://example.local)"
CACHE_TTL_SECONDS = 60 * 60 * 24 * 3  # 3 jours


def _cache_path(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return PAGES_DIR / f"{digest}.json"


def fetch_url(url: str, ttl: int = CACHE_TTL_SECONDS) -> Optional[Dict[str, str]]:
    cache_file = _cache_path(url)
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < ttl:
            import json

            with cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    doc = Document(response.text)
    title = doc.title() or url
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    record = {"url": url, "title": title.strip(), "text": text.strip()}

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    import json

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return record


__all__ = ["fetch_url"]
