from rank_bm25 import BM25Okapi
from backend.vector_store import vector_store

class HybridSearch:
    def __init__(self):
        self.bm25 = None
        self.corpus = []

    def build(self, texts):
        self.corpus = texts
        tokenized = [doc.split() for doc in texts]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query, k=5):
        bm25_scores = self.bm25.get_scores(query.split())
        vector_results = vector_store.search(query, k)

        # Combine results (simple merge for demo)
        combined = list(set(vector_results))
        return combined[:k]

hybrid_search = HybridSearch()
