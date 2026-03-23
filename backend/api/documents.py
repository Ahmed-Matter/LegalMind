from fastapi import APIRouter, UploadFile, File, Depends
import os

from database import cursor, conn
from ingestion.pdf_processor import extract_pages, split_text_by_page, process_pdf
from vectorstore.vector_store import add_chunks
from services.hybrid_search import build_bm25
from core.security import verify_token


docs_router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@docs_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(verify_token)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    cursor.execute(
        "INSERT INTO documents(filename, filepath) VALUES (?,?)",
        (file.filename, file_path)
    )

    document_id = cursor.lastrowid
    conn.commit()

    pages = extract_pages(file_path)
    chunks = process_pdf(file_path)

    add_chunks(chunks, document_id)
    build_bm25()

    return {
        "id": document_id,
        "filename": file.filename
    }


@docs_router.get("/documents")
def list_documents(user=Depends(verify_token)):

    cursor.execute("SELECT id, filename, filepath FROM documents")

    return [
        {"id": r[0], "filename": r[1], "path": r[2]}
        for r in cursor.fetchall()
    ]