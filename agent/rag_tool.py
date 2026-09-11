from agent.rag import RAGEngine


class RAGTool:

    def __init__(self, document):

        self.rag = RAGEngine(document)

    def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5
    ):

        results = self.rag.search(
            query,
            top_k=top_k
        )

        return results