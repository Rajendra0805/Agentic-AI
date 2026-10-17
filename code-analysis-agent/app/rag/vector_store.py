import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:

    def __init__(self, storage_path: str):

        self.storage_path = Path(
            storage_path
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.index = None
        self.metadata = []

    def build(
        self,
        embeddings,
        metadata
    ):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        self.metadata = metadata

    def search(
        self,
        query_embedding,
        top_k: int = 5
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

            results.append({
                "score": float(score),
                "metadata": self.metadata[index]
            })

        return results