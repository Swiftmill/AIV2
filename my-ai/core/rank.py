from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import INDEX_PATH, load_json, save_json, slugify


def tokenize(text: str) -> List[str]:
    return [token for token in text.lower().split() if token]


class DocumentStore:
    def __init__(self, index_path: Path = INDEX_PATH):
        self.index_path = index_path
        self.documents: List[Dict[str, str]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.bm25: Optional[BM25Okapi] = None
        self._load()

    def _load(self) -> None:
        data = load_json(self.index_path)
        if data and isinstance(data.get("documents"), list):
            self.documents = data["documents"]
        self._build_indices()

    def _persist(self) -> None:
        save_json(self.index_path, {"documents": self.documents})

    def _build_indices(self) -> None:
        if not self.documents:
            self.vectorizer = None
            self.tfidf_matrix = None
            self.bm25 = None
            return

        texts = [doc.get("text", "") for doc in self.documents]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        tokenized = [tokenize(text) for text in texts]
        self.bm25 = BM25Okapi(tokenized) if tokenized else None

    def add_document(self, title: str, text: str, url: str, source_type: str = "local") -> Dict[str, str]:
        if not text.strip():
            raise ValueError("Text must not be empty")
        for doc in self.documents:
            if doc.get("url") == url and doc.get("text") == text:
                return doc
        doc_id = slugify(f"{title}-{len(self.documents)}")
        record = {
            "id": doc_id,
            "title": title,
            "text": text,
            "url": url,
            "source_type": source_type,
        }
        self.documents.append(record)
        self._persist()
        self._build_indices()
        return record

    def update_document(self, doc_id: str, text: str) -> None:
        for doc in self.documents:
            if doc["id"] == doc_id:
                doc["text"] = text
                break
        self._persist()
        self._build_indices()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, object]]:
        if not query.strip() or not self.documents:
            return []
        if not self.vectorizer or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        cosine_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        bm25_scores = np.zeros(len(self.documents))
        if self.bm25 is not None:
            bm25_scores = np.array(self.bm25.get_scores(tokenize(query)))
            if np.max(bm25_scores) > 0:
                bm25_scores = bm25_scores / np.max(bm25_scores)

        if np.max(cosine_scores) > 0:
            cosine_scores = cosine_scores / np.max(cosine_scores)

        combined = 0.6 * cosine_scores + 0.4 * bm25_scores

        scored_docs = []
        for idx, doc in enumerate(self.documents):
            score = float(combined[idx])
            scored_docs.append({"document": doc, "score": score})

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]


__all__ = ["DocumentStore", "tokenize"]
