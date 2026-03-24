def build_prompt(question, context, history=None):

    history_text = ""
    if history:
        history_text = "\n".join(
            f"{m['role']}: {m['text']}" for m in history
        )

    return f"""
You are a legal AI assistant.

Answer ONLY using the provided context.

Extract the FULL and COMPLETE answer.

IMPORTANT RULES:
- Include ALL details (a, b, c if exist)
- Do NOT summarize
- Do NOT shorten
- Do NOT return only part of the answer
- Do NOT return titles only

Context:
{context}

Question:
{question}

Full Answer:
"""