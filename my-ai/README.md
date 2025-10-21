# My Local Answering AI

Une IA locale simple qui recherche, lit et résume des documents locaux ou du web (via DuckDuckGo) sans utiliser de LLM externes.

## Installation (VS Code / Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Ouvrez ensuite `ui/index.html` dans votre navigateur (l'API tourne sur http://localhost:8000).

## Fonctionnalités
- Chat FastAPI `/chat`
- Ingestion de pages web `/ingest_url`
- Ingestion de fichiers `/ingest_file`
- Mémoire locale basée sur des fichiers
- Résumés extractifs (TextRank), recherche TF-IDF/BM25

## Ingestion
- `/ingest_url` : fournir un JSON `{ "url": "https://exemple.com" }`
- `/ingest_file` : requête multipart contenant un fichier `.txt`, `.md` ou `.pdf`

Les documents sont stockés dans `knowledge/` et indexés dans `data/index.json`.

## Limites
- Résumé extractif uniquement
- Pas de génération créative
- Nécessite l'autorisation de recherche web pour interroger Internet
