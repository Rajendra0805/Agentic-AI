def search_knowledge_base(
    rag_engine,
    query,
    top_k=3
):

    results = rag_engine.search(
        query,
        top_k=top_k,
        score_threshold=0.35
    )

    if not results:

        return {
            "found": False,
            "evidence": [],
            "message": (
                "No sufficiently relevant "
                "document content was found."
            )
        }

    evidence = []

    for result in results:

        evidence.append({
            "page_number": result.get(
                "page_number"
            ),

            "text": result.get(
                "text",
                ""
            ),

            "rerank_score": round(
                result.get(
                    "rerank_score",
                    0
                ),
                4
            )
        })

    return {
        "found": True,
        "evidence": evidence
    }