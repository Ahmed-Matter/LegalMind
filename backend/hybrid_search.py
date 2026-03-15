from rank_bm25 import BM25Okapi
from vector_store import all_chunks
import numpy as np

bm25 = None
tokenized_corpus = []


def build_bm25():

    global bm25
    global tokenized_corpus

    # no chunks available
    if len(all_chunks) == 0:
        bm25 = None
        return

    tokenized_corpus = [
        chunk["text"].lower().split()
        for chunk in all_chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)



def keyword_search(query, k=10):

    global bm25

    if bm25 is None:
        return []

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:k]

    results = []

    for idx in top_indices:
        if idx < len(all_chunks):
            results.append(all_chunks[idx])

    return results