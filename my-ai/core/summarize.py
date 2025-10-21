from __future__ import annotations

from typing import List

from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer


def summarize_text(text: str, max_sentences: int = 3) -> str:
    if not text.strip():
        return ""
    parser = PlaintextParser.from_string(text, Tokenizer("french"))
    summarizer = TextRankSummarizer()
    sentences = summarizer(parser.document, max_sentences)
    return " ".join(str(sentence) for sentence in sentences)


def compress_answer(sentences: List[str], max_length: int = 700) -> str:
    answer = " \n".join(sentence.strip() for sentence in sentences if sentence.strip())
    if len(answer) <= max_length:
        return answer
    return answer[: max_length - 3].rstrip() + "..."


__all__ = ["summarize_text", "compress_answer"]
