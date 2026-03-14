from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import numpy as np
import os
import requests
from memory_store import add_message, get_memory
from context_utils import extract_best_sentence
from vector_store import add_chunks, search, load_chunks
from embeddings import create_embedding
from llm_service import generate_answer
from reranker import rerank
from database import cursor, conn
from pdf_processor import extract_pages, split_text_by_page
import uuid

app = FastAPI()

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# STARTUP
# -----------------------------------

@app.on_event("startup")
def startup():

    load_chunks()


# -----------------------------------
# ROOT
# -----------------------------------

@app.get("/")
def root():
    return {"message": "LegalMind API running"}


# -----------------------------------
# LOGIN (Auth0)
# -----------------------------------

AUTH0_DOMAIN = "dev-dh4evfod0ajyzd7e.us.auth0.com"
CLIENT_ID = "uV1mOqT9ERsyU7ngLw9cVJjjf5laxTTB"
CLIENT_SECRET = "gnoiVE7C3ppRTh_qow_zV3Q_5Ze-DDH4waUtZAm6W3KOZ7dDta2QQZQmU406FBT1"


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
# -----------------------------------
# UPLOAD
# -----------------------------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # save document metadata
    cursor.execute(
        "INSERT INTO documents(filename, filepath) VALUES (?,?)",
        (file.filename, file_path)
    )

    document_id = cursor.lastrowid

    conn.commit()

    pages = extract_pages(file_path)

    chunks = split_text_by_page(pages)

    add_chunks(chunks, document_id)
    print("Pages extracted:", len(pages))
    print("Chunks created:", len(chunks))
    return {"message": "uploaded"}

# -----------------------------------
# DOCUMENT LIST
# -----------------------------------

@app.get("/documents")
def list_documents():

    cursor.execute("SELECT id, filename, filepath FROM documents")

    rows = cursor.fetchall()

    docs = []

    for r in rows:
        docs.append({
            "id": r[0],
            "filename": r[1],
            "path": r[2]
        })

    return docs


# -----------------------------------
# CHAT
# -----------------------------------
@app.post("/chat")
def chat(question: str):

    query_embedding = create_embedding(question)
    query_embedding = np.array([query_embedding]).astype("float32")

   
    # vector search
    results = search(query_embedding, k=20)

    if len(results) == 0:

        prompt = f"""
        You are a legal AI assistant.

        Answer the question clearly.

        Question:
        {question}

        Answer:
        """

        sources = []

    else:

        # rerank results
        ranked_texts = rerank(question, [r["text"] for r in results])
        #ranked_texts = ranked_texts(dict.fromkeys(ranked_texts))

        # limit context (VERY IMPORTANT)
        context = ranked_texts[0][:600]

        prompt = f"""
                Answer the question using the context.

                Context:
                {context}

                Question:
                {question}

                Answer in one short sentence.
                """

        sources = [
            f"Document {r['document_id']} page {r['page']}"
            for r in results[:3]
        ]
    print("CONTEXT SENT TO LLM:")
    print(context)
    answer = generate_answer(prompt)

    print("Retrieved chunks:", len(results))

    return {
        "answer": answer,
        "sources": sources
    }


# -----------------------------------
# STREAM ANSWER
# -----------------------------------

async def stream_answer(prompt, session_id="default"):

    answer = generate_answer(prompt)

    if not answer:
        answer = "I could not generate a response."

    add_message(session_id, "assistant", answer)

    yield {"event": "message", "data": answer}
    yield {"event": "end", "data": "[DONE]"}
# -----------------------------------
# STREAM CHAT
# -----------------------------------
# @app.get("/chat-stream")
# async def chat_stream(question: str):

#     query_embedding = create_embedding(question)
#     query_embedding = np.array([query_embedding]).astype("float32")

#     results = search(query_embedding, k=20)

#     if len(results) == 0:

#         prompt = f"""
#         Question: {question}

#         Answer briefly.
#         """

#     else:

#         ranked_texts = rerank(question, [r["text"] for r in results])

#         # take best chunk only
#         context = ranked_texts[0][:600]

#         sentence = extract_best_sentence(context, question)

#         prompt = f"""
#         Context: {sentence}

#         Question: {question}

#         Answer briefly in one sentence.
#         """
#     print("BEST CHUNK:", context)
#     generator = stream_answer(prompt)
#     print("generator :", generator)
#     return EventSourceResponse(generator, ping=15000)

@app.get("/chat-stream")
async def chat_stream(question: str, session_id: str = "default"):

    add_message(session_id, "user", question)

    query_embedding = create_embedding(question)
    query_embedding = np.array([query_embedding]).astype("float32")

    results = search(query_embedding, k=20)

    if len(results) == 0:

        context = ""

    else:

        ranked_texts = rerank(question, [r["text"] for r in results])

        context = ranked_texts[0][:600]

    sentence = extract_best_sentence(context, question) or context

    # build memory text
    history = get_memory(session_id)

    history_text = ""

    for m in history:
        history_text += f"{m['role']}: {m['text']}\n"

    prompt = f"""
You are a helpful assistant.

Conversation history:
{history_text}

Context:
{sentence}

Question:
{question}

Answer briefly:
"""

    generator = stream_answer(prompt)

    return EventSourceResponse(generator)