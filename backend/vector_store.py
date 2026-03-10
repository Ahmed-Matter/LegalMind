import faiss
import numpy as np
from embeddings import create_embedding

dimension =384

index=faiss.IndexFlatL2(dimension)

documents=[]

def add_chunks(chunks):
    global index
    global documents

    vectors=[]

    for chunk in chunks:
        embedding=create_embedding(chunk)

        vectors.append(embedding)
        documents.append(chunk)

    vectors = np.array(vectors).astype("float32")

    index.add(vectors)

def search(query_embedding,k=3):
    if len(documents)==0 :
        return []

    query_embedding=np.array([query_embedding]).astype("float32")

    distances,indices = index.search(query_embedding,k)

    result=[]

    for i in indices[0]:
        result.append(documents[i])

    return result