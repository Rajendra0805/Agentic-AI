
import argparse
import json
import sys
from pathlib import Path

from app.agent.code_review_agent import CodeReviewAgent
from app.review.review_report import ReviewReportGenerator
from app.review.review_evaluator import (
    ExpectedFinding,
    ReviewEvaluator,
)
from app.review.evidence_verifier import EvidenceVerifier


def build_expected_findings() -> list[ExpectedFinding]:
    """
    Baseline evaluation dataset for the sample repository.

    Adjust file paths, keywords, and severity labels to match
    your test repository and human-reviewed expectations.
    """
    return [
        ExpectedFinding(
            category="Security",
            file_path=(
                "Customer.Infrastructure/"
                "CustomerRepository.cs"
            ),
            keyword="password",
            expected_severity="High",
        ),
        ExpectedFinding(
            category="Architecture",
            file_path=(
                "Customer.Api/Controllers/"
                "CustomerController.cs"
            ),
            keyword="business logic",
            expected_severity="Medium",
        ),
        ExpectedFinding(
            category="Reliability",
            file_path=(
                "Customer.Api/Services/"
                "CustomerService.cs"
            ),
            keyword="null",
            expected_severity="Medium",
        ),
    ]


def save_json(data: dict, output_path: str) -> str:
    """Save a JSON object and return its absolute file path."""
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return str(path)


def print_review_evaluation(evaluation: dict) -> None:
    """Print detection metrics and unmatched findings."""
    print("\n" + "=" * 60)
    print("CODE REVIEW EVALUATION")
    print("=" * 60)

    print(f"Expected findings : {evaluation['expected_count']}")
    print(f"Actual findings   : {evaluation['actual_count']}")
    print(f"True positives    : {evaluation['true_positives']}")
    print(f"False positives   : {evaluation['false_positives']}")
    print(f"False negatives   : {evaluation['false_negatives']}")
    print(f"Precision         : {evaluation['precision']:.1%}")
    print(f"Recall            : {evaluation['recall']:.1%}")
    print(f"F1 score          : {evaluation['f1_score']:.1%}")

    missing = evaluation.get("missing_findings", [])

    if missing:
        print("\nMissing expected findings:")

        for finding in missing:
            print(
                f"- {finding['category']}: "
                f"{finding['file_path']} "
                f"(keyword: {finding['keyword']})"
            )

    unmatched = evaluation.get(
        "unmatched_actual_findings", []
    )

    if unmatched:
        print("\nUnmatched actual findings:")

        for finding in unmatched:
            print(
                f"- [{finding['category']}] "
                f"{finding['title']} "
                f"({finding['file_path']})"
            )


def print_evidence_results(evidence_result: dict) -> None:
    """Print evidence verification outcomes."""
    print("\n" + "=" * 60)
    print("EVIDENCE VERIFICATION")
    print("=" * 60)

    print(
        f"Total findings    : "
        f"{evidence_result['total_findings']}"
    )
    print(
        f"Verified          : "
        f"{evidence_result['verified_count']}"
    )
    print(
        f"Unverified        : "
        f"{evidence_result['unverified_count']}"
    )

    for result in evidence_result["results"]:
        print(
            f"\n[{result['status'].upper()}] "
            f"{result['file_path']}"
        )
        print(f"Finding: {result['title']}")
        print(f"Reason: {result['reason']}")


def print_severity_results(severity_result: dict) -> None:
    """Print severity accuracy for matched expected findings."""
    print("\n" + "=" * 60)
    print("SEVERITY EVALUATION")
    print("=" * 60)

    print(
        f"Matched findings  : "
        f"{severity_result['checked_findings']}"
    )
    print(
        f"Correct severities: "
        f"{severity_result['correct_severities']}"
    )
    print(
        f"Incorrect         : "
        f"{severity_result['incorrect_severities']}"
    )

    accuracy = severity_result["severity_accuracy"]

    if accuracy is None:
        print(
            "Severity accuracy: N/A "
            "(no matched findings with expected severity)"
        )
    else:
        print(f"Severity accuracy: {accuracy:.1%}")

    for match in severity_result["matches"]:
        status = "PASS" if match["correct"] else "FAIL"

        print(
            f"[{status}] {match['keyword']}: "
            f"expected={match['expected_severity']}, "
            f"actual={match['actual_severity']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Code Review Agent, generate a Markdown "
            "report, verify evidence, and evaluate review quality."
        )
    )

    parser.add_argument(
        "repository_path",
        help="Path to the .NET repository to review.",
    )

    parser.add_argument(
        "question",
        nargs="?",
        default=(
            "Review this repository for security, architecture, "
            "performance, maintainability, reliability, and code "
            "quality issues. Report evidence-backed findings with "
            "file paths and line numbers when available. Return "
            "structured findings consistent with the review schema."
        ),
        help="Review instructions or question for the agent.",
    )

    parser.add_argument(
        "--report",
        default="reports/code-review-report.md",
        help="Path for the generated Markdown report.",
    )

    parser.add_argument(
        "--evaluation",
        default="reports/code-review-evaluation.json",
        help="Path for the evaluation JSON file.",
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Generate the report without running evaluations.",
    )

    args = parser.parse_args()

    repository_path = Path(
        args.repository_path
    ).resolve()

    if not repository_path.is_dir():
        print(
            f"Error: Repository directory not found: "
            f"{repository_path}",
            file=sys.stderr,
        )
        return 2

    print("=" * 60)
    print("CODE REVIEW AGENT — DAY 6, STAGE 6")
    print("=" * 60)
    print(f"Repository: {repository_path}")
    print(f"Question: {args.question}")

    try:
        # 1. Run the Code Review Agent.
        agent = CodeReviewAgent(
            repository_path=str(repository_path)
        )

        review = agent.run(
            user_question=args.question
        )

        # 2. Generate and save the Markdown report.
        report_generator = ReviewReportGenerator()

        report = report_generator.generate(review)

        report_path = report_generator.save(
            report,
            args.report,
        )

        print("\n" + "=" * 60)
        print("GENERATED CODE REVIEW REPORT")
        print("=" * 60)
        print(report)
        print(f"\nReport saved: {report_path}")

        # Stop after report generation if evaluation was disabled.
        if args.skip_evaluation:
            print("\nEvaluation skipped.")
            print("Code review workflow completed.")
            return 0

        # 3. Evaluate finding detection.
        expected_findings = build_expected_findings()

        evaluator = ReviewEvaluator()

        evaluation = evaluator.evaluate(
            review,
            expected_findings,
        )

        print_review_evaluation(evaluation)

        # 4. Verify evidence against repository source files.
        evidence_result = EvidenceVerifier(
            str(repository_path)
        ).verify(review)

        print_evidence_results(evidence_result)

        # 5. Evaluate severity for matched expected findings.
        severity_result = evaluator.evaluate_severity(
            review,
            expected_findings,
        )

        print_severity_results(severity_result)

        # 6. Combine results into one evaluation artifact.
        combined_evaluation = {
            "repository": str(repository_path),
            "reviewed_scope": review.reviewed_scope,
            "summary": review.summary,
            "finding_detection": evaluation,
            "evidence_verification": evidence_result,
            "severity_evaluation": severity_result,
        }

        evaluation_path = save_json(
            combined_evaluation,
            args.evaluation,
        )

        print(f"\nEvaluation saved: {evaluation_path}")
        print("\nCode review workflow completed.")

        return 0

    except Exception as exc:
        print(
            f"\nCode review workflow failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
