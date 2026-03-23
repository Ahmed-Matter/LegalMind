import re

def rewrite_question(question, history):

    # no history → return as is
    if not history:
        return question

    last_user_question = ""

    # get last user question
    for m in reversed(history):
        if m["role"] == "user":
            last_user_question = m["text"]
            break

    q = question.lower()

    # 🔥 handle pronouns
    if "it" in q and last_user_question:
        return f"{last_user_question}. {question}"

    # 🔥 normalize common legal queries
    if "probation" in q:
        return question + " probation period employee trial period"

    if "salary" in q:
        return question + " salary compensation employee payment"

    return question