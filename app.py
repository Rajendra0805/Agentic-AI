from agent.document_loader import load_document
from agent.rag import RAGEngine
from agent.rag_agent import DocumentAgent


DOCUMENT_PATH = (
    "documents/"
    "enterprise_document_analysis_test.pdf"
)


def main():

    print("Loading document...")

    document = load_document(
        DOCUMENT_PATH
    )

    print(
        f"Document pages: "
        f"{len(document['pages'])}"
    )

    print("\nBuilding RAG index...")

    rag = RAGEngine(
        document
    )

    print("\nCreating agent...")

    agent = DocumentAgent(
        document,
        rag
    )

    print("\nDocument Analysis Agent ready.")

    while True:

        question = input(
            "\nYou: "
        )

        if question.lower() in [
            "exit",
            "quit"
        ]:
            break

        answer = agent.run(
            question
        )

        print(
            f"\nAgent: {answer}"
        )


if __name__ == "__main__":
    main()