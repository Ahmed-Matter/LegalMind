import numpy as np

from embeddings import create_embedding
from vectorstore.vector_store import search
from services.hybrid_search import hybrid_search
from services.reranker import rerank


class RetrievalService:

   
    # QUERY EXPANSION (optional boost)
    # ----------------------------
    def expand_query(self, question):
        return question  # keep generic (no hardcoding)

    # ----------------------------
    # FILTER BAD CHUNKS
    # ----------------------------
    def is_valid_chunk(self, text):
        text = text.strip()

        if len(text) < 40:
            return False

        if text.count("_") > 5:
            return False

        if len(text.split()) < 5:
            return False

        return True

    # ----------------------------
    # GENERIC KEYWORD SCORING
    # ----------------------------
    def keyword_score(self, results, question):

        q_words = set(question.lower().split())

        for r in results:
            text = r["text"].lower()
            score = sum(1 for w in q_words if w in text)
            r["keyword_score"] = score

        return sorted(results, key=lambda x: x["keyword_score"], reverse=True)

    # ----------------------------
    # GENERIC SECTION BOOST
    # ----------------------------
    def section_boost(self, results, question):

        q_words = set(question.lower().split())

        for r in results:

            text = r["text"].lower()

            # first few words = pseudo-title
            title = " ".join(text.split()[:5])

            score = 0

            for w in q_words:
                if w in title:
                    score += 2

            r["boost"] = score

        return sorted(results, key=lambda x: x.get("boost", 0), reverse=True)

    # ----------------------------
    # MAIN RETRIEVAL PIPELINE
    # ----------------------------
    def retrieve(self, question, k=50):

        # 1️⃣ expand query (generic)
        expanded_question = self.expand_query(question)

        # 2️⃣ embedding
        query_embedding = create_embedding(expanded_question)
        query_embedding = np.array([query_embedding]).astype("float32")

        # 3️⃣ vector search
        vector_results = search(query_embedding, k)

        # 4️⃣ hybrid search
        combined_results = hybrid_search(expanded_question, vector_results, k)

        combined_results = combined_results[:100]

        # 5️⃣ filter invalid chunks
        combined_results = [
            r for r in combined_results
            if self.is_valid_chunk(r["text"])
        ]

        if not combined_results:
            return []

        # 6️⃣ keyword scoring (generic)
        combined_results = self.keyword_score(combined_results, question)

        # 7️⃣ section boost (generic)
        combined_results = self.section_boost(combined_results, question)

        # 8️⃣ deterministic ordering
        preselected = sorted(combined_results, key=lambda r: r["text"])[:50]

        texts = [r["text"] for r in preselected]

        # 9️⃣ rerank (semantic)
        ranked_texts = rerank(expanded_question, texts)

        text_to_chunk = {r["text"]: r for r in preselected}

        ranked_chunks = [
            text_to_chunk[t]
            for t in ranked_texts
            if t in text_to_chunk
        ]

        # debug (optional)
        print("\n=== RETRIEVED CHUNKS ===")
        for r in ranked_chunks[:5]:
            print(r["text"][:200])

        return ranked_chunks