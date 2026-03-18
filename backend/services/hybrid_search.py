import re
from rank_bm25 import BM25Okapi
from vectorstore.vector_store import all_chunks
import numpy as np


bm25 = None
tokenized_corpus = []


def tokenize(text):
    return re.findall(r"\w+", text.lower())


def build_bm25():

    global bm25
    global tokenized_corpus

    if len(all_chunks) == 0:
        bm25 = None
        return

    tokenized_corpus = [
        tokenize(chunk["text"])
        for chunk in all_chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)


def keyword_search(query, k=10):

    global bm25

    if bm25 is None:
        return []

    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:k]

    results = []

    for idx in top_indices:
        if idx < len(all_chunks):
            results.append(all_chunks[idx])

    return results

def hybrid_search(query, vector_result, k=10):
    keyword_result = keyword_search(query,k)

    combined= vector_result + keyword_result

    seen=set()
    unique_results=[]

    for chunk in combined :
        chunk_id = chunk.get("id") or chunk["text"]

        if chunk_id not in seen:
            seen.add(chunk_id)
            unique_results.append(chunk)

    return unique_results[:k]