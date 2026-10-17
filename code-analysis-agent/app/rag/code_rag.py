from pathlib import Path

from app.rag.code_chunker import CodeChunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore


class CodeRAG:

    def __init__(
        self,
        repository_path: str,
        index_path: str = "data/code_index"
    ):

        self.repository_path = Path(
            repository_path
        ).resolve()

        self.chunker = CodeChunker()

        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store = VectorStore(
            index_path
        )

        self.chunks = []

    def build_index(self):

        print("[RAG] Reading repository...")

        all_chunks = []

        extensions = {
            ".cs",
            ".csproj",
            ".json",
            ".xml",
            ".config",
            ".yml",
            ".yaml"
        }

        for path in self.repository_path.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in extensions:
                continue

            if any(
                ignored in path.parts
                for ignored in {
                    ".git",
                    "bin",
                    "obj",
                    "node_modules",
                    ".venv"
                }
            ):
                continue

            try:

                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:
                continue

            relative_path = str(
                path.relative_to(
                    self.repository_path
                )
            )

            chunks = self.chunker.chunk_file(
                relative_path,
                content
            )

            all_chunks.extend(chunks)

        print(
            f"[RAG] Created "
            f"{len(all_chunks)} chunks."
        )

        texts = [
            chunk.content
            for chunk in all_chunks
        ]

        print(
            "[RAG] Creating embeddings..."
        )

        embeddings = (
            self.embedding_service.embed(
                texts
            )
        )

        metadata = []

        for chunk in all_chunks:

            metadata.append({
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content
            })

        self.vector_store.build(
            embeddings,
            metadata
        )

        self.chunks = all_chunks

        print("[RAG] Index built successfully.")

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.35
    ):

        query_embedding = (
            self.embedding_service.embed(
                [query]
            )[0]
        )

        results = self.vector_store.search(
            query_embedding,
            top_k
        )
        formatted_results = []

        for result in results:

            if result["score"] < score_threshold:
                continue

            metadata = result["metadata"]

            formatted_results.append({
                "score": result["score"],
                "file_path": metadata["file_path"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
                "content": metadata["content"]
            })

        return formatted_results