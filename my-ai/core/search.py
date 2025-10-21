from __future__ import annotations

from typing import List

from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> List[dict]:
    results: List[dict] = []
    if not query:
        return results
    with DDGS() as ddgs:
        for hit in ddgs.text(query, max_results=max_results):
            url = hit.get("href") or hit.get("url")
            if not url:
                continue
            if not url.startswith(("http://", "https://")):
                continue
            results.append(
                {
                    "title": hit.get("title") or url,
                    "url": url,
                    "snippet": hit.get("body", ""),
                }
            )
    return results


__all__ = ["web_search"]
