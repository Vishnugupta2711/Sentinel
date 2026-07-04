from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from rag.models.schemas import RAGResult, RegulationDocument
from rag.engine.core import rag_engine

router = APIRouter(prefix="/rag", tags=["RAG Agent"])


@router.get("/search", response_model=RAGResult)
async def search(q: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=20)):
    return rag_engine.retrieve(q, top_k=top_k)


@router.get("/documents", response_model=List[RegulationDocument])
async def list_documents(source: Optional[str] = Query(None)):
    docs = rag_engine.documents
    if source:
        docs = [d for d in docs if d.source.value == source.upper()]
    return docs


@router.post("/reload")
async def reload_kb():
    rag_engine.reload_kb()
    return {"status": "reloaded", "documents": len(rag_engine.documents), "incidents": len(rag_engine.incidents)}
