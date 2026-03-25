from fastapi import APIRouter, Depends, Query
from sse_starlette.sse import EventSourceResponse

from services.query_service import rewrite_question
from services.prompt_service import build_prompt
from services.retrieval_service import RetrievalService
from services.llm_service import generate_answer
from services.memory_store import add_message, get_memory
from core.security import verify_token, verify_token_from_query
from services.context_builder import build_context


router = APIRouter()

retrieval_service = RetrievalService()


 #
# CHAT (normal)
 #
@router.post("/chat")
def chat(question: str, user=Depends(verify_token)):

    ranked_chunks = retrieval_service.retrieve(question, k=50)

    session_id = "default"
    history = get_memory(session_id)

    if not ranked_chunks:
        context = ""
        sources = []
    else:
        context = build_context(ranked_chunks, question)

    sources = [
        {
            "document_id": c["document_id"],
            "page": c["page"],
            "text": c["text"][:300]  # preview for highlight
        }
        for c in ranked_chunks[:3]
    ]

    # prompt
    prompt = build_prompt(question, context, history)

    
    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources
    }


 #
# STREAM CHAT
 #
@router.get("/chat-stream")
async def chat_stream(
    question: str,
    session_id: str = "default",
    token: str = Query(...)
):

    verify_token_from_query(token)

    history = get_memory(session_id)

    # rewrite BEFORE adding current question
    rewritten_question = rewrite_question(question, history)

    # now store original question (not rewritten!)
    add_message(session_id, "user", question)
    ranked_chunks = retrieval_service.retrieve(rewritten_question, k=50)

    if not ranked_chunks:
        context = ""
    else:
        context = build_context(ranked_chunks, question)

   

    history_text = "\n".join(
        f"{m['role']}: {m['text']}" for m in history
    )

    prompt = build_prompt(question, context, history)
    generator = stream_answer(prompt)
    print("\n=== CONTEXT ===")
    print(context)
    return EventSourceResponse(generator)


 #
# STREAM HELPER
 #
async def stream_answer(prompt, session_id="default"):

    answer = generate_answer(prompt)

    if not answer:
        answer = "I could not generate a response."

    add_message(session_id, "assistant", answer)

    yield {"event": "message", "data": answer}
    yield {"event": "end", "data": "[DONE]"}