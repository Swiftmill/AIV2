from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.pipeline import QAPipeline

app = FastAPI(title="Mon IA Locale", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = QAPipeline()


class ChatRequest(BaseModel):
    message: str
    allow_web: Optional[bool] = False


class ChatResponse(BaseModel):
    answer: str
    sources: list
    confidence: float


class URLRequest(BaseModel):
    url: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message vide")
    result = pipeline.compose_answer(payload.message, allow_web=payload.allow_web or False)
    return ChatResponse(**result)


@app.post("/ingest_url")
def ingest_url(payload: URLRequest) -> dict:
    record = pipeline.ingest_url(payload.url)
    if not record:
        raise HTTPException(status_code=400, detail="Impossible de récupérer l'URL")
    return {"detail": f"URL ingérée : {record['title']}"}


@app.post("/ingest_file")
async def ingest_file(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")
    try:
        record = pipeline.ingest_file(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"detail": f"Fichier ingéré : {record['title']}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
