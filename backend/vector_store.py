import faiss
import numpy as np

# embedding dimension
dimension = 384

# vector index
index = faiss.IndexFlatL2(dimension)

# store document chunks
chunks = []


def add_chunks(text_chunks):

    global chunks

    from embeddings import create_embedding

    embeddings = []

    for chunk in text_chunks:
        emb = create_embedding(chunk)
        embeddings.append(emb)

        chunks.append({
            "text": chunk
        })

    index.add(np.array(embeddings))


def search(query_embedding, k=5):

    if len(chunks) == 0:
        return []

    D, I = index.search(query_embedding, k)

    results = []

    for idx in I[0]:
        if idx < len(chunks):
            results.append(chunks[idx])

    return results