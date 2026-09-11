from agent.chunker import chunk_document
from agent.embeddings import EmbeddingModel
from agent.vector_store import VectorStore
from agent.retriever import Retriever


class RAGEngine:

    def __init__(self, document):

        self.document = document

        print("\nCreating document chunks...")

        self.chunks = chunk_document(
            document
        )

        print(
            f"Created {len(self.chunks)} chunks."
        )

        self.embedding_model = (
            EmbeddingModel()
        )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        print(
            "Creating embeddings..."
        )

        embeddings = (
            self.embedding_model
            .encode(texts)
        )

        dimension = embeddings.shape[1]

        print(
            f"Embedding dimension: {dimension}"
        )

        self.vector_store = VectorStore(
            dimension
        )

        self.vector_store.add(
            embeddings,
            self.chunks
        )

        from agent.hybrid_retriever import (
            HybridRetriever
        )
        self.retriever = Retriever(
            self.embedding_model,
            self.vector_store
        )
        self.hybrid_retriever = HybridRetriever(
            self.document,
            self.retriever
        )

        print(
            "RAG index created successfully."
        )

    def search(
        self,
        query,
        top_k=5,
        score_threshold=0.35
    ):

        print(
            f"\n[RAG] Query: {query}"
        )

        results = self.hybrid_retriever.search(
            query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        print(
            f"[RAG] Retrieved: {len(results)} chunks"
        )

        for result in results:

            print(
                f"[RAG] "
                f"Page={result['page_number']} "
                f"RRF={result.get('rrf_score', 0):.6f} "
                f"VectorRank={result.get('vector_rank')} "
                f"KeywordRank={result.get('keyword_rank')}"
            )

        return results