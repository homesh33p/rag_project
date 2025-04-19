from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query
from app.db.database import init_db

app = FastAPI(
    title="RAG API",
    description="Retrieval Augmented Generation API with pgvector",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}

app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
