from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vectorstore.vector_store import add_chunks, search, load_chunks
from services.hybrid_search import build_bm25, keyword_search
from services.retrieval_service import RetrievalService

from fastapi.middleware.cors import CORSMiddleware


# refactoring
from api.chat import router as chat_router  
from api.auth import auth_router
from api.documents import docs_router

app = FastAPI()
retrieval_service = RetrievalService()
app.include_router(chat_router) #refator
app.include_router(auth_router)
app.include_router(docs_router)




origins = [
    "http://localhost:5173",  # React Vite
    "http://127.0.0.1:5173",
    "http://localhost:3000"   # react dev.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():

    load_chunks()

    build_bm25()





