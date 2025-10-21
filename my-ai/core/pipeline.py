from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .crawl import fetch_url
from .memory import MemoryStore
from .rank import DocumentStore
from .search import web_search
from .summarize import compress_answer, summarize_text
from .utils import KNOWLEDGE_DIR, sanitize_filename


class QAPipeline:
    def __init__(self, store: Optional[DocumentStore] = None, memory: Optional[MemoryStore] = None):
        self.store = store or DocumentStore()
        self.memory = memory or MemoryStore()

    def _detect_memory_commands(self, message: str) -> Optional[Dict[str, str]]:
        remember_note = re.search(r"souviens-toi que (.+?) est (.+)", message, flags=re.IGNORECASE)
        if remember_note:
            key = remember_note.group(1).strip()
            value = remember_note.group(2).strip()
            if key and value:
                return {"type": "note", "key": key, "value": value}

        remember_fact = re.search(r"souviens-toi de (.+)", message, flags=re.IGNORECASE)
        if remember_fact:
            return {"type": "fact", "value": remember_fact.group(1).strip()}
        return None

    def ingest_text(self, title: str, text: str, url: str = "local") -> Dict[str, str]:
        return self.store.add_document(title=title, text=text, url=url, source_type="local")

    def ingest_url(self, url: str) -> Optional[Dict[str, str]]:
        payload = fetch_url(url)
        if not payload:
            return None
        record = self.store.add_document(payload["title"], payload["text"], payload["url"], source_type="web")
        return record

    def ingest_file(self, filename: str, content: bytes) -> Dict[str, str]:
        sanitized = sanitize_filename(filename)
        target_path = KNOWLEDGE_DIR / sanitized
        target_path.write_bytes(content)
        text = self._extract_text(target_path)
        if not text.strip():
            raise ValueError("Le fichier ne contient pas de texte exploitable")
        return self.ingest_text(title=sanitized, text=text, url=str(target_path))

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        data = path.read_bytes()
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(path)
                pages = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages)
            except Exception:
                return ""
        return data.decode("utf-8", errors="ignore")

    def retrieve(self, query: str, allow_web: bool = False) -> Dict[str, object]:
        results = self.store.search(query, top_k=5)
        confidence = results[0]["score"] if results else 0.0

        if allow_web and confidence < 0.35:
            web_results = web_search(query, max_results=3)
            for item in web_results:
                fetched = fetch_url(item["url"])
                if fetched and len(fetched.get("text", "")) > 200:
                    try:
                        self.store.add_document(
                            title=fetched["title"],
                            text=fetched["text"],
                            url=fetched["url"],
                            source_type="web",
                        )
                    except ValueError:
                        continue
            results = self.store.search(query, top_k=5)
            confidence = results[0]["score"] if results else 0.0

        return {"results": results, "confidence": confidence}

    def compose_answer(self, query: str, allow_web: bool = False) -> Dict[str, object]:
        memory_command = self._detect_memory_commands(query)
        if memory_command:
            if memory_command["type"] == "fact":
                self.memory.add_fact(memory_command["value"])
            elif memory_command["type"] == "note":
                self.memory.remember(memory_command["key"], memory_command["value"])

        retrieval = self.retrieve(query, allow_web=allow_web)
        results = retrieval["results"]
        confidence = retrieval["confidence"]

        if not results:
            answer = "Incertitude élevée."
            sources: List[Dict[str, str]] = []
        else:
            top_texts = [hit["document"]["text"] for hit in results[:3]]
            merged_text = "\n\n".join(top_texts)
            summary = summarize_text(merged_text, max_sentences=4)
            if not summary:
                summary = merged_text[:400]
            notes = self.memory.recall()
            note_sentences = [f"Note: {key} -> {value}" for key, value in notes.items()]
            answer = compress_answer([summary] + note_sentences)
            sources = [
                {
                    "title": hit["document"].get("title") or hit["document"].get("url"),
                    "url": hit["document"].get("url"),
                }
                for hit in results[:3]
            ]

        self.memory.log_interaction(query, answer)
        return {"answer": answer, "sources": sources, "confidence": confidence}


__all__ = ["QAPipeline"]
