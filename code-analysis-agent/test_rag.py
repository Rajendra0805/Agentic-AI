from app.rag.code_rag import CodeRAG


def main():

    repository_path = "sample-repository"

    rag = CodeRAG(
        repository_path
    )

    rag.build_index()

    query = (
        "Where is authentication configured?"
    )

    results = rag.search(
        query,
        top_k=5
    )

    print()
    print("=" * 60)
    print("RAG SEARCH RESULTS")
    print("=" * 60)

    for result in results:

        metadata = result["metadata"]

        print()
        print(
            f"Score: {result['score']:.3f}"
        )

        print(
            f"File: {metadata['file_path']}"
        )

        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )

        print(
            metadata["content"][:500]
        )


if __name__ == "__main__":
    main()