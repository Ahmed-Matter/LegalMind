from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body,Query
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
from hybrid_search import build_bm25, keyword_search
from auth import verify_token, verify_token_from_query

app = FastAPI()

# -----------------------------------
# CORS
# -----------------------------------

from fastapi.middleware.cors import CORSMiddleware

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
# -----------------------------------
# STARTUP
# -----------------------------------

@app.on_event("startup")
def startup():

    load_chunks()

    build_bm25()


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
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "AUTH_SECRET"
API_AUDIENCE="AUTH_API"



@app.post("/login")
def login(data: dict = Body(...)):

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": API_AUDIENCE,
        "scope": "openid profile email",
        "realm": "Username-Password-Authentication"
    }

    headers = {
        "content-type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        # return Auth0 error to help debugging
        try:
            error_data = res.json()
        except:
            error_data = {"error": res.text}

        raise HTTPException(
            status_code=401,
            detail=error_data
        )

    token_data = res.json()

    return {
        "access_token": token_data.get("access_token"),
        "id_token": token_data.get("id_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type")
    }

# login enhanced
# from fastapi import Body

# @app.post("/login")
# def login(data: dict = Body(...)):

#     email = data.get("email")
#     password = data.get("password")

#     url = f"https://{AUTH0_DOMAIN}/oauth/token"

#     payload = {
#         "grant_type": "password",
#         "username": email,
#         "password": password,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "audience": "https://legalmind-api",
#         "scope": "openid profile email"
#     }

#     headers = {"content-type": "application/json"}

#     res = requests.post(url, json=payload, headers=headers)

#     if res.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     return res.json()

# -----------------------------------
# UPLOAD
# -----------------------------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload")
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
    chunks = split_text_by_page(pages)

    add_chunks(chunks, document_id)
    build_bm25()

    return {
        "id": document_id,
        "filename": file.filename,
        "path": file_path
    }

# -----------------------------------
# DOCUMENT LIST
# -----------------------------------

@app.get("/documents")
def list_documents(user=Depends(verify_token)):

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
def chat(question: str, user=Depends(verify_token)):

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
    answer = generate_answer(prompt)


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
async def chat_stream(question: str,session_id: str = "default",token: str = Query(...)):
    
    #print('token in chat stream ${token}')
    user = verify_token_from_query(token)
    add_message(session_id, "user", question)

    query_embedding = create_embedding(question)
    query_embedding = np.array([query_embedding]).astype("float32")

    # --- hybrid retrieval ---
    vector_results = search(query_embedding, k=10)
    keyword_results = keyword_search(question, k=10)

    results = vector_results + keyword_results

    # remove duplicates
    unique = {}
    for r in results:
        unique[r["text"]] = r

    results = list(unique.values())

    # --- rerank results ---
    if len(results) == 0:
        context = ""
    else:
        ranked_texts = rerank(question, [r["text"] for r in results])

        # use top chunks instead of single sentence
        context = "\n".join(ranked_texts[:3])[:1000]

    # --- conversation history ---
    history = get_memory(session_id)

    history_text = ""
    for m in history:
        history_text += f"{m['role']}: {m['text']}\n"

    # --- prompt ---
    prompt = f"""
You are a helpful assistant.

Use the context to answer the question.

Conversation history:
{history_text}

Context:
{context}

Question:
{question}

Answer in one clear sentence.
"""

    # debug (optional but useful)

    generator = stream_answer(prompt)

    return EventSourceResponse(generator)