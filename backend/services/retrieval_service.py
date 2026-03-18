import numpy as np

from embeddings import create_embedding
from vectorstore.vector_store import search
from services.hybrid_search import keyword_search
from services.reranker import rerank


class RetrievalService:

    def retrieve(self, question, k=10):

        query_embedding = create_embedding(question)
        query_embedding = np.array([query_embedding]).astype("float32")

        # vector search
        vector_results = search(query_embedding, k)

        # keyword search
        keyword_results = keyword_search(question, k)

        # combine
        combined_results = vector_results + keyword_results

        # deduplicate
        unique = {}
        for r in combined_results:
            unique[r["text"]] = r

        combined_results = list(unique.values())

        if not combined_results:
            return []

        # rerank
        ranked_texts = rerank(
            question,
            [r["text"] for r in combined_results]
        )
        #get chunks sources
        text_to_chunks = {r["text"]: r for r in combined_results}

        ranked_chunks = [text_to_chunks[text] for text in ranked_texts 
                         if text in text_to_chunks]

        return ranked_chunks