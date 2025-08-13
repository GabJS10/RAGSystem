import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim: int = 1536):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []      # Lista de chunks
        self.metadata = []   # Lista de metadatos por chunk

    def add(self, embedding: list[float], text: str, meta: dict):
        self.index.add(np.array([embedding], dtype=np.float32))
        self.texts.append(text)
        self.metadata.append(meta)

    def search(self, embedding: list[float], top_k: int = 5):
        D, I = self.index.search(np.array([embedding], dtype=np.float32), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadata[idx]
                })
        return results
