from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(question,chunks):
    pairs=[]

    for chunk in chunks:
        pairs.append((question,chunk))

    scores= reranker.predict(pairs)
    ranked=list(zip(chunks,scores))

    ranked.sort(key=lambda x:x[1], reverse=True)

    return [r[0] for r in ranked[:3]]