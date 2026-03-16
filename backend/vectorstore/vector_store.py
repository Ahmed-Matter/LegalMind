import faiss
import numpy as np
import os
from database import cursor, conn
from embeddings import create_embedding

all_chunks = []
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

    global index
    global all_chunks

    vectors = []

    for chunk in chunks:

        vector = create_embedding(chunk["text"])

        vectors.append(vector)

        all_chunks.append({
            "text": chunk["text"],
            "document_id": document_id,
            "page": chunk["page"]
        })

    vectors = np.array(vectors).astype("float32")

    index.add(vectors)

def search(query_vector, k=10):

    distances, indices = index.search(query_vector, k)

    results = []

    for i in indices[0]:
        if i < len(all_chunks):
            results.append(all_chunks[i])

    return results

def load_chunks():

    global all_chunks

    # load from database if you have that
    # or rebuild from stored metadata

    print("Chunks loaded:", len(all_chunks))