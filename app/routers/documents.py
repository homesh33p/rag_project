from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse

router = APIRouter(tags=["documents"])

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new document in the database."""
    db_document = Document(
        title=document.title,
        content=document.content,
        # embedding would be generated and added here in a real implementation
    )
    
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    
    return db_document

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get a list of documents from the database."""
    result = await db.execute(select(Document).offset(skip).limit(limit))
    documents = result.scalars().all()
    return documents

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific document by ID."""
    result = await db.execute(select(Document).filter(Document.id == document_id))
    document = result.scalar_one_or_none()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document
