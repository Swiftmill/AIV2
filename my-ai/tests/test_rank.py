import tempfile
import unittest
from pathlib import Path

try:
    from core.rank import DocumentStore
except Exception as exc:  # pragma: no cover
    DocumentStore = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


@unittest.skipIf(DocumentStore is None, f"DocumentStore indisponible: {IMPORT_ERROR}")
class DocumentStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.index_path = Path(self.tempdir.name) / "index.json"
        self.index_path.write_text('{"documents": []}', encoding="utf-8")
        self.store = DocumentStore(index_path=self.index_path)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_add_and_search(self):
        self.store.add_document("Doc1", "Python est un langage", "local")
        self.store.add_document("Doc2", "FastAPI est un framework", "local")
        results = self.store.search("framework web", top_k=2)
        self.assertTrue(results)
        titles = [res["document"]["title"] for res in results]
        self.assertIn("Doc2", titles)


if __name__ == "__main__":
    unittest.main()
