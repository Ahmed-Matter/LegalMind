from fastapi import FastAPI,UploadFile,File
from database import cursor, conn
import os
from pdf_processor import extract_text,split_text
from vector_store import add_chunks
from embeddings import create_embedding
from vector_store import search
from llm_service import generate_answer

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LegalMind API running"}

users = {
    "admin@test.com": {
        "id": 1,
        "name": "Admin User",
        "role": "Admin"
    },
    "associate@test.com": {
        "id": 2,
        "name": "Associate User",
        "role": "Associate"
    }
}

from fastapi import FastAPI,HTTPException



@app.post('/login')
def login(email:str):
    if(email in users):
        return users[email]
    raise HTTPException(status_code=401,detail="user not found")

from fastapi import Depends

def require_admin(user: dict):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_location = f"uploads/{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())
        text = extract_text(file_location)
        chunks= split_text(text)
        add_chunks(chunks)

    cursor.execute(
        "INSERT INTO documents (filename, filepath) VALUES (?, ?)",
        (file.filename, file_location)
    )

    conn.commit()

    return {"filename": file.filename}

@app.get("/documents")
def list_documents():

    cursor.execute("SELECT * FROM documents")

    rows = cursor.fetchall()

    docs = []

    for r in rows:
        docs.append({
            "id": r[0],
            "filename": r[1],
            "path": r[2]
        })

    return docs

@app.post("/chat")
def chat(question:str):
    query_embeddig= create_embedding(question)
    results=search(query_embeddig)
    if len(results) == 0:
        return {"answer": "No documents available. Please upload a document first."}
    context="\n".join(results)

    prompt=f""" use the following documents to answer the question Context:{context} Question:{question} answer:"""

    answer=generate_answer(prompt)

    return {"Question answer":answer}

