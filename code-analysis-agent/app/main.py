import sys

from app.agent.code_analysis_agent import CodeAnalysisAgent


def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python -m app.main "
            "<repository_path> "
            "<question>"
        )

        return

    repository_path = sys.argv[1]

    question = " ".join(sys.argv[2:])

    print()
    print("=" * 60)
    print("CODE ANALYSIS AGENT")
    print("=" * 60)

    print()
    print(f"[Repository] {repository_path}")
    print(f"[Question]   {question}")

    try:

        agent = CodeAnalysisAgent(
            repository_path
        )

        answer = agent.run(question)

        print()
        print("=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        print(answer)

    except Exception as exc:

        print()
        print("[ERROR]")
        print(str(exc))


if __name__ == "__main__":
    main()