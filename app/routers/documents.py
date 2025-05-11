from fastapi import APIRouter,UploadFile,File
import os

from app.documents import SimplifiedUserGuideProcessor

router = APIRouter(tags=["documents"])

# @router.post("/documents/upload-custom-document")
# async def upload_custom_document(file: UploadFile = File(...)):
#     """Upload and process userguide CSV - no model needed."""
    
#     # Save uploaded file
#     temp_path = f"/tmp/{file.filename}"
#     with open(temp_path, "wb") as buffer:
#         buffer.write(await file.read())
    
#     # Process and store
#     processor = SimplifiedUserGuideProcessor()
#     vectorstore = processor.process_csv_to_vectorstore(temp_path)
    
#     # Clean up
#     os.remove(temp_path)
    
#     return {"status": "success", "message": "Userguide stored in pgvector"}



