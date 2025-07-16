from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService


router = APIRouter()

rag_service = RAGService()

class IngestionResponse(BaseModel):
    message: str
    num_chunks_ingested: int

@router.post("/ingest", response_model=IngestionResponse)
async def handle_document_ingestion(
    user_id: str = Form(...), 
    product_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Receives a PDF and metadata and passes it to the RAGService for ingestion.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        num_chunks = rag_service._ingest_document(
            file=file.file, 
            user_id=user_id,
            product_id=product_id
        )
        return IngestionResponse(
            message="Document processed and indexed successfully.",
            num_chunks_ingested=num_chunks
        )
    except Exception as e:
        print(f"Error occurred during ingestion: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during document processing.")