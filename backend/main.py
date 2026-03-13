from fastapi import FastAPI,UploadFile,File
from reranker import rerank
from database import cursor, conn
import os
from pdf_processor import extract_text,split_text
from vector_store import add_chunks
from embeddings import create_embedding
from vector_store import search
from llm_service import generate_answer
from sse_starlette.sse import EventSourceResponse
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt
import requests
from fastapi import Depends

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



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""@app.post('/login')
def login(email:str):
    if(email in users):
        return users[email]
    raise HTTPException(status_code=401,detail="user not found")"""

AUTH0_DOMAIN = "dev-dh4evfod0ajyzd7e.us.auth0.com"
CLIENT_ID = "uV1mOqT9ERsyU7ngLw9cVJjjf5laxTTB"
CLIENT_SECRET = "gnoiVE7C3ppRTh_qow_zV3Q_5Ze-DDH4waUtZAm6W3KOZ7dDta2QQZQmU406FBT1"

# IMPORTANT: must match your Auth0 database connection name
REALM = "LegalMind-Users"

@app.post("/login")
def login(email: str, password: str):

    url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "username": email,
        "password": password,
        
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid profile email"
    }

    headers = {"content-type": "application/json"}

    res = requests.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        print(res.text)  # helpful for debugging
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = res.json()

    return {
        "access_token": token_data["access_token"],
        "id_token": token_data.get("id_token"),
        "expires_in": token_data["expires_in"],
        "token_type": token_data["token_type"]
    }

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
def chat(question: str):

    query_embedding = create_embedding(question)
    query_embedding = np.array([query_embedding]).astype("float32")

    results = search(query_embedding, k=10)
    if len(results) > 0:
        #print(results)
        context = "\n".join([r["text"] for r in results])
        prompt=f""" use the following legal documents to asnwer: context:{context}
                question:{question} 
                Answer clearly """
    else:
        prompt = f"""
                Question: {question}
                Answer:
                """
    answer = generate_answer(prompt)

    return {"answer": answer}

async def stream_answer(prompt):

    answer = generate_answer(prompt)

    words = answer.split()

    for word in words:

        yield {
            "event": "message",
            "data": word + " "
        }

@app.get("/chat-stream")
async def chat_stream(question: str):

    query_embedding = create_embedding(question)

    results = search(query_embedding, k=10)

    results=rerank(question,[r["text"] for r in results])

    context = "\n".join(results)

    prompt = f""" You are a legal assistant.Use ONLY the information in the context. If the answer is not present say:
                "I cannot find this information in the uploaded documents."

                Context:{context}

                Question:{question}

                Answer step-by-step:
                1. Identify relevant clause
                2. Extract key information
                3. Provide final answer
                """

    generator = stream_answer(prompt)

    return EventSourceResponse(generator)

