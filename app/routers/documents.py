from fastapi import APIRouter, Depends, HTTPException, status, UploadFile,File
from typing import List
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.documents import SimplifiedUserGuideProcessor

router = APIRouter(tags=["documents"])

# @router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# async def create_document(document: DocumentCreate, db: AsyncSession = Depends(get_db)):
#     """Create a new document in the database."""
#     db_document = Document(
#         title=document.title,
#         content=document.content,
#         # embedding would be generated and added here in a real implementation
#     )
    
#     db.add(db_document)
#     await db.commit()
#     await db.refresh(db_document)
    
#     return db_document

# @router.get("/documents", response_model=List[DocumentResponse])
# async def get_documents(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
#     """Get a list of documents from the database."""
#     result = await db.execute(select(Document).offset(skip).limit(limit))
#     documents = result.scalars().all()
#     return documents

# @router.get("/documents/{document_id}", response_model=DocumentResponse)
# async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
#     """Get a specific document by ID."""
#     result = await db.execute(select(Document).filter(Document.id == document_id))
#     document = result.scalar_one_or_none()
    
#     if document is None:
#         raise HTTPException(status_code=404, detail="Document not found")
    
#     return document

@router.post("/documents/upload-userguide")
async def upload_userguide(file: UploadFile = File(...)):
    """Upload and process userguide CSV - no model needed."""
    
    # Save uploaded file
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Process and store
    processor = SimplifiedUserGuideProcessor()
    vectorstore = processor.process_csv_to_vectorstore(temp_path)
    
    # Clean up
    os.remove(temp_path)
    
    return {"status": "success", "message": "Userguide stored in pgvector"}

# Query endpoint - also doesn't need a model
@router.post("documents/query/userguide")
async def query_userguide(query: str, k: int = 3):
    """Query the userguide vector store."""
    
    processor = SimplifiedUserGuideProcessor()
    
    # Search
    results = processor.vectorstore.similarity_search(query, k=k)
    
    # Return results
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]