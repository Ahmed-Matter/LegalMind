import faiss
import numpy as np
import os
from database import cursor, conn
from embeddings import create_embedding

# single source of truth
all_chunks = []

dimension = 384

# load or create index
if os.path.exists("vector.index"):
    index = faiss.read_index("vector.index")
else:
    index = faiss.IndexFlatL2(dimension)


# ----------------------------
# SAVE INDEX
# ----------------------------
def save_index():
    faiss.write_index(index, "vector.index")


# ----------------------------
# LOAD CHUNKS FROM DB
# ----------------------------
def load_chunks():

    global all_chunks
    global index

    cursor.execute("SELECT id, document_id, page, text FROM chunks")
    rows = cursor.fetchall()

    all_chunks = []
    embeddings = []

    for r in rows:

        chunk = {
            "id": r[0],
            "document_id": r[1],
            "page": r[2],
            "text": r[3]
        }

        all_chunks.append(chunk)

        # IMPORTANT: same embedding logic as add_chunks
        emb = create_embedding(chunk["text"])
        embeddings.append(emb)

    if len(embeddings) > 0:

        vectors = np.array(embeddings).astype("float32")

        index.reset()
        index.add(vectors)

        print("Loaded chunks:", len(all_chunks))

        save_index()
    else:
        print("No chunks found in DB")


# ----------------------------
# ADD CHUNKS
# ----------------------------
def add_chunks(chunks, document_id):

    global index
    global all_chunks

    vectors = []

    for chunk in chunks:

        text = f"{chunk.get('title','')}\n{chunk['text']}"

        if not is_valid_chunk(text):
            continue

        # embedding
        vector = create_embedding(text)
        vectors.append(vector)

        # store in DB
        cursor.execute(
            "INSERT INTO chunks (document_id, page, text) VALUES (?, ?, ?)",
            (document_id, chunk.get("page", 0), text)
        )

        # store in memory
        all_chunks.append({
            "text": text,
            "document_id": document_id,
            "page": chunk.get("page", 0)
        })

    conn.commit()

    print("=== SAMPLE CHUNKS ===")
    for c in all_chunks[:5]:
        print(c["text"][:200])
        
    if len(vectors) > 0:
        vectors = np.array(vectors).astype("float32")
        index.add(vectors)

        save_index()

        print("Added chunks:", len(vectors))

# ----------------------------
# SEARCH
# ----------------------------
def search(query_vector, k=20):

    if index.ntotal == 0:
        return []

    distances, indices = index.search(query_vector, k)

    results = []

    for i in indices[0]:
        if 0 <= i < len(all_chunks):
            results.append(all_chunks[i])

    return results

def is_valid_chunk(text):

    text = text.strip()

    # too short
    if len(text) < 40:
        return False

    # mostly underscores / noise
    if text.count("_") > 5:
        return False

    # no meaningful words
    words = text.split()
    if len(words) < 5:
        return False

    return True