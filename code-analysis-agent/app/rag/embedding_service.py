from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        print(
            f"[Embedding] Loading model: {model_name}"
        )

        self.model = SentenceTransformer(
            model_name
        )

    def embed(
        self,
        texts: list[str]
    ):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )