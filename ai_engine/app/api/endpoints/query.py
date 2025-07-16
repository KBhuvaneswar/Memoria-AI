from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str # 'user' or 'ai'
    content: str

class QueryRequest(BaseModel):
    query: str
    user_id: str
    product_id: str
    chat_history: Optional[List[ChatMessage]] = None

class QueryResponse(BaseModel):
    answer: str

# Router
router = APIRouter()

# A single & shared instance of our RAG service
rag_service = RAGService()

@router.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):    
    response = rag_service.search(query=request.query, user_id=request.user_id, product_id=request.product_id)
    
    if "Sorry" in response or "couldn't find" in response:
        raise HTTPException(status_code=404, detail=response)

    return QueryResponse(answer=response)