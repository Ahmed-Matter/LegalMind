def build_prompt(question, context, history=None):

    history_text = ""
    if history:
        history_text = "\n".join(
            f"{m['role']}: {m['text']}" for m in history
        )

    return f"""
You are a legal AI assistant.

Answer using ONLY the provided context.

Extract the full definition clearly.

Do NOT summarize too much.
Do NOT guess.

Context:
{context}

Question:
{question}

Answer:
"""