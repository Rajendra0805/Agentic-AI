from agent.keyword_retriever import (
    KeywordRetriever
)
from agent.reranker import (
    Reranker
)

class HybridRetriever:

    def __init__(
        self,
        document,
        semantic_retriever
    ):

        self.document = document
        
        self.semantic_retriever = (
            semantic_retriever
        )

        self.keyword_retriever = (
            KeywordRetriever(document)
        )

        self.reranker = Reranker()

    def search(
        self,
        query,
        top_k=5,
        score_threshold=0.35
    ):

        print(
            f"\n[HYBRID] Query: {query}"
        )

        # ---------------------------------
        # Vector / semantic retrieval
        # ---------------------------------

        semantic_results = (
            self.semantic_retriever.retrieve(
                query,
                top_k=10,
                score_threshold=score_threshold
            )
        )

        print(
            "[HYBRID] Semantic candidates:",
            len(semantic_results)
        )

        # ---------------------------------
        # Keyword retrieval
        # ---------------------------------

        keyword_results = (
            self.keyword_retriever.search(
                query,
                max_results=10
            )
        )

        print(
            "[HYBRID] Keyword candidates:",
            len(keyword_results)
        )

        # ---------------------------------
        # RRF
        # ---------------------------------

        candidate_results = self._rrf_merge(
            semantic_results,
            keyword_results,
            top_k=5
        )
        print(
            f"[HYBRID] RRF candidates: "
            f"{len(candidate_results)}"
        )

        reranked_results = self.reranker.rerank(
            query,
            candidate_results,
            top_k=top_k
        )

        print(
            f"[HYBRID] Reranked results: "
            f"{len(reranked_results)}"
        )

        for result in reranked_results:

            print(
                f"[RERANK] "
                f"Page={result['page_number']} "
                f"Score={result['rerank_score']:.4f}"
            )

        return reranked_results

    def _rrf_merge(
        self,
        semantic_results,
        keyword_results,
        top_k,
        k=60
    ):

        merged = {}

        # =================================
        # Vector results
        # =================================

        for rank, result in enumerate(
            semantic_results,
            start=1
        ):

            page = result.get(
                "page_number"
            )

            if page not in merged:

                merged[page] = {
                    "page_number": page,
                    "text": result.get(
                        "text",
                        ""
                    ),
                    "vector_rank": rank,
                    "keyword_rank": None,
                    "rrf_score": 0.0
                }

            merged[page][
                "vector_rank"
            ] = rank

            merged[page][
                "rrf_score"
            ] += 1 / (
                k + rank
            )

        # =================================
        # Keyword results
        # =================================

        for rank, result in enumerate(
            keyword_results,
            start=1
        ):

            page = result.get(
                "page_number"
            )

            if page not in merged:

                merged[page] = {
                    "page_number": page,
                    "text": result.get(
                        "text",
                        ""
                    ),
                    "vector_rank": None,
                    "keyword_rank": rank,
                    "rrf_score": 0.0
                }

            else:

                merged[page][
                    "keyword_rank"
                ] = rank

            merged[page][
                "rrf_score"
            ] += 1 / (
                k + rank
            )

        # =================================
        # Sort
        # =================================

        results = list(
            merged.values()
        )

        results.sort(
            key=lambda x:
                x["rrf_score"],
            reverse=True
        )

        return results[:top_k]