import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension):

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.chunks = []

    def add(
        self,
        embeddings,
        chunks
    ):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        self.index.add(
            embeddings
        )

        self.chunks.extend(
            chunks
        )

    def search(
        self,
        query_embedding,
        top_k=5,
        score_threshold=0.35
    ):

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        scores, indexes = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indexes[0]
        ):

            if index == -1:
                continue

            score = float(score)

            if score < score_threshold:
                continue

            chunk = self.chunks[index]

            results.append({
                "score": score,
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "text": chunk["text"]
            })

        return results