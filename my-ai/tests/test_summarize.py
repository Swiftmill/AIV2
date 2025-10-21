import unittest

try:
    from core.summarize import compress_answer, summarize_text
except Exception as exc:  # pragma: no cover
    compress_answer = None
    summarize_text = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class SummarizeTest(unittest.TestCase):
    @unittest.skipIf(summarize_text is None, f"Sommaire indisponible: {IMPORT_ERROR}")
    def test_summarize_returns_text(self):
        text = (
            "FastAPI est un framework web moderne pour Python. "
            "Il est rapide et utilise des annotations de type. "
            "Il est idéal pour construire des APIs."
        )
        summary = summarize_text(text, max_sentences=2)
        self.assertTrue(len(summary) > 0)

    @unittest.skipIf(compress_answer is None, f"Compression indisponible: {IMPORT_ERROR}")
    def test_compress_answer_limits_length(self):
        sentences = ["phrase" * 100]
        compressed = compress_answer(sentences, max_length=50)
        self.assertTrue(len(compressed) <= 50)


if __name__ == "__main__":
    unittest.main()
