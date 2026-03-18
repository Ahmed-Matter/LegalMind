from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse

from services.retrieval_service import RetrievalService
from services.llm_service import generate_answer
from services.memory_store import add_message, get_memory
from core.security import verify_token, verify_token_from_query


router = APIRouter()

retrieval_service = RetrievalService()


# ----------------------------
# CHAT (normal)
# ----------------------------
@router.post("/chat")
def chat(question: str, user=Depends(verify_token)):

    ranked_chunks = retrieval_service.retrieve(question, k=20)

    if not ranked_chunks:
        prompt = f"""
You are a legal AI assistant.

Answer the question clearly.

Question:
{question}

Answer:
"""
        sources = []

    else:
        context = ranked_chunks[0][:600]

        prompt = f"""
Answer the question using the context.

Context:
{context}

Question:
{question}

Answer in one short sentence.
"""
        sources = [f"document {c['document_id']} page {c['page']}"
                   for c in ranked_chunks[:3]]

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources
    }


# ----------------------------
# STREAM CHAT
# ----------------------------
@router.get("/chat-stream")
async def chat_stream(
    question: str,
    session_id: str = "default",
    token: str = Query(...)
):

    verify_token_from_query(token)

    add_message(session_id, "user", question)

    ranked_chunks = retrieval_service.retrieve(question, k=20)

    if not ranked_chunks:
        context = ""
    else:
        if not ranked_chunks:
            context = ""
        else:
            context = "\n".join(
        c["text"] for c in ranked_chunks[:3])[:1000]

    history = get_memory(session_id)

    history_text = "\n".join(
        f"{m['role']}: {m['text']}" for m in history
    )

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

    generator = stream_answer(prompt)

    return EventSourceResponse(generator)


# ----------------------------
# STREAM HELPER
# ----------------------------
async def stream_answer(prompt, session_id="default"):

    answer = generate_answer(prompt)

    if not answer:
        answer = "I could not generate a response."

    add_message(session_id, "assistant", answer)

    yield {"event": "message", "data": answer}
    yield {"event": "end", "data": "[DONE]"}