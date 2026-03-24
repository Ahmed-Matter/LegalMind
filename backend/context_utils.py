import re

def extract_best_sentences(context, question, top_n=3):

    q = question.lower()

    #   if asking definition → return FULL section
    if "what is" in q or "define" in q:

        # take first 2–3 lines directly
        parts = re.split(r'(?<=[\.\n])', context)

        selected = []
        for p in parts:
            p = p.strip()
            if p:
                selected.append(p)
            if len(selected) >= 3:
                break

        return " ".join(selected)

    # fallback (scoring)
    sentences = re.split(r'(?<=[\.\n])', context)

    keywords = set(q.split())

    scored = []

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        score = sum(1 for w in keywords if w in s.lower())
        scored.append((s, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    best_sentences = [s for s, _ in scored[:top_n]]

    return " ".join(best_sentences)