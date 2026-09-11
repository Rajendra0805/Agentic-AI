from agent.document_loader import load_document
from agent.agent import run_agent
from agent.llm import ask_agent, ask_llm
from agent.rag_prompt import build_rag_prompt

def main():

    document_path = "documents/enterprise_document_analysis_test.pdf"

    print("====================================")
    print("     DOCUMENT ANALYSIS AGENT")
    print("====================================")

    print("\nLoading document...")

    document = load_document(
        document_path
    )
    from agent.rag import RAGEngine
    rag = RAGEngine(
        document
    )

    while True:

        query = input(
            "\nEnter RAG search query "
            "(type 'exit' to quit): "
        ).strip()

        if query.lower() == "exit":

            print("\nGoodbye!")

            break

        if not query:

            print("Please enter a search query.")

            continue

        results = rag.search(
            query,
            top_k=5
        )
        prompt = build_rag_prompt(
            query,
            results
        )

        answer = ask_llm([
            {
                "role": "user",
                "content": prompt
            }
        ])

        print("\n========== ANSWER ==========")

        print(answer)
        # print("\n========== RETRIEVED CHUNKS ==========")

        # for result in results:

        #     print(
        #         f"\nPage: {result['page_number']}"
        #     )

        #     print(
        #         f"Score: {result['score']:.4f}"
        #     )

        #     print(
        #         f"Text: {result['text']}"
        #     )

    # print("Document loaded successfully.")

    # print(
    #     f"File: {document['file_name']}"
    # )

    # print(
    #     f"Pages: {document['page_count']}"
    # )

    # while True:

    #     question = input(
    #         "\nAsk a question "
    #         "(type 'exit' to quit): "
    #     )

    #     if question.lower() == "exit":

    #         print("\nGoodbye!")

    #         break

    #     print("\nAgent is working...")

    #     answer = run_agent(
    #         document,
    #         question
    #     )

    #     print("\n====================================")
    #     print("ANSWER")
    #     print("====================================")

    #     print(answer)


if __name__ == "__main__":
    main()