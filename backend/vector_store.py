import faiss
import numpy as np
import os
from database import cursor, conn

dimension = 384
chunks_store = []

if os.path.exists("vector.index"):
    index = faiss.read_index("vector.index")
else:
    index = faiss.IndexFlatL2(dimension)


def save_index():
    faiss.write_index(index, "vector.index")


def load_chunks():

    global chunks_store

    from embeddings import create_embedding

    cursor.execute("SELECT id, document_id, page, text FROM chunks")

    rows = cursor.fetchall()

    chunks_store = []

    embeddings = []

    for r in rows:

        chunk = {
            "id": r[0],
            "document_id": r[1],
            "page": r[2],
            "text": r[3]
        }

        chunks_store.append(chunk)

        emb = create_embedding(chunk["text"])
        embeddings.append(emb)

    if len(embeddings) > 0:

        vectors = np.array(embeddings).astype("float32")

        index.reset()
        index.add(vectors)

        print("Loaded chunks:", len(chunks_store))

        save_index()


def add_chunks(chunks, document_id):

    global chunks_store

    from embeddings import create_embedding

    embeddings = []

    for chunk in chunks:

        text = chunk["text"].strip()
        page = chunk["page"]

        if len(text) < 20:
            continue

        emb = create_embedding(text)
        embeddings.append(emb)

        cursor.execute(
            "INSERT INTO chunks(document_id,page,text) VALUES(?,?,?)",
            (document_id, page, text)
        )

        chunk_id = cursor.lastrowid

        chunks_store.append({
            "id": chunk_id,
            "document_id": document_id,
            "page": page,
            "text": text
        })

    conn.commit()

    if len(embeddings) == 0:
        return

    vectors = np.array(embeddings).astype("float32")

    index.add(vectors)

    print("Vectors added:", len(vectors))

    save_index()


def search(query_embedding, k=5):

    if len(chunks_store) == 0:
        print("No chunks available")
        return []

    D, I = index.search(query_embedding, k)

    results = []

    for idx in I[0]:

        if idx < len(chunks_store):
            results.append(chunks_store[idx])

    print("Search results:", len(results))

    return results