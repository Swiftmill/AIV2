import json
import re
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PAGES_DIR = DATA_DIR / "pages"
MEMORY_DIR = DATA_DIR / "memory"
LOGS_DIR = DATA_DIR / "logs"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
INDEX_PATH = DATA_DIR / "index.json"
MEMORY_PATH = MEMORY_DIR / "default.json"


def ensure_directories() -> None:
    for path in [DATA_DIR, PAGES_DIR, MEMORY_DIR, LOGS_DIR, KNOWLEDGE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def sanitize_filename(filename: str) -> str:
    name = slugify(Path(filename).stem)
    suffix = Path(filename).suffix.lower()
    return f"{name}{suffix}" if name else f"document{suffix or '.txt'}"


ensure_directories()
