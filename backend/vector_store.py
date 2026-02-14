import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)

class VectorStore:
    def __init__(self):
        self.index = None
        self.texts = []

    def add_documents(self, chunks):
        embeddings = model.encode(chunks)
        dim = embeddings.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(np.array(embeddings))
        self.texts.extend(chunks)

    def search(self, query, k=5):
        query_vec = model.encode([query])
        D, I = self.index.search(np.array(query_vec), k)
        return [self.texts[i] for i in I[0]]

vector_store = VectorStore()
