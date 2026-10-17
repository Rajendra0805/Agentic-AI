
from dataclasses import dataclass

from app.models.code_review_models import CodeReviewResult


@dataclass(frozen=True)
class ExpectedFinding:
    category: str
    file_path: str
    keyword: str
    expected_severity: str | None = None



class ReviewEvaluator:

    def evaluate(
        self,
        review: CodeReviewResult,
        expected_findings: list[ExpectedFinding],
    ) -> dict:
        """
        Compare actual findings with expected findings.

        One actual finding can match at most one expected finding.
        Matching is intentionally simple and deterministic.
        """

        actual_findings = review.findings
        matched_actual_indexes = set()
        matched_expected_indexes = set()
        matches = []

        for expected_index, expected in enumerate(
            expected_findings
        ):
            for actual_index, actual in enumerate(
                actual_findings
            ):
                if actual_index in matched_actual_indexes:
                    continue

                same_category = (
                    str(actual.category).casefold()
                    == expected.category.casefold()
                )

                actual_path = actual.file_path.replace(
                    "\\", "/"
                ).casefold()

                expected_path = expected.file_path.replace(
                    "\\", "/"
                ).casefold()

                same_file = (
                    actual_path == expected_path
                    or actual_path.endswith("/" + expected_path)
                    or expected_path.endswith("/" + actual_path)
                )

                searchable_text = (
                    f"{actual.title} {actual.description}"
                ).casefold()

                keyword_found = (
                    expected.keyword.casefold()
                    in searchable_text
                )

                if same_category and same_file and keyword_found:
                    matched_actual_indexes.add(actual_index)
                    matched_expected_indexes.add(expected_index)

                    matches.append({
                        "expected": expected.keyword,
                        "actual_title": actual.title,
                        "file_path": actual.file_path,
                    })

                    break

        true_positives = len(matched_expected_indexes)
        false_positives = (
            len(actual_findings) - len(matched_actual_indexes)
        )
        false_negatives = (
            len(expected_findings) - true_positives
        )

        precision = (
            true_positives / (true_positives + false_positives)
            if true_positives + false_positives
            else 0.0
        )

        recall = (
            true_positives / (true_positives + false_negatives)
            if true_positives + false_negatives
            else 0.0
        )

        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        missing = [
            {
                "category": expected.category,
                "file_path": expected.file_path,
                "keyword": expected.keyword,
            }
            for index, expected in enumerate(expected_findings)
            if index not in matched_expected_indexes
        ]

        unmatched_actual = [
            {
                "category": str(actual.category),
                "title": actual.title,
                "file_path": actual.file_path,
            }
            for index, actual in enumerate(actual_findings)
            if index not in matched_actual_indexes
        ]

        return {
            "expected_count": len(expected_findings),
            "actual_count": len(actual_findings),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "matches": matches,
            "missing_findings": missing,
            "unmatched_actual_findings": unmatched_actual,
        }

    
def evaluate_severity(
    self,
    review,
    expected_findings: list[ExpectedFinding],
) -> dict:
    """Measure severity accuracy for matched expected findings."""

    matched = []
    checked = 0
    correct = 0

    for expected in expected_findings:
        if expected.expected_severity is None:
            continue

        for actual in review.findings:
            same_category = (
                str(actual.category).casefold()
                == expected.category.casefold()
            )

            actual_path = actual.file_path.replace(
                "\\", "/"
            ).casefold()

            expected_path = expected.file_path.replace(
                "\\", "/"
            ).casefold()

            same_file = (
                actual_path == expected_path
                or actual_path.endswith("/" + expected_path)
                or expected_path.endswith("/" + actual_path)
            )

            searchable_text = (
                f"{actual.title} {actual.description}"
            ).casefold()

            if (
                same_category
                and same_file
                and expected.keyword.casefold() in searchable_text
            ):
                checked += 1

                actual_severity = str(actual.severity)
                is_correct = (
                    actual_severity.casefold()
                    == expected.expected_severity.casefold()
                )

                if is_correct:
                    correct += 1

                matched.append({
                    "keyword": expected.keyword,
                    "expected_severity": expected.expected_severity,
                    "actual_severity": actual_severity,
                    "correct": is_correct,
                })

                break

    return {
        "checked_findings": checked,
        "correct_severities": correct,
        "incorrect_severities": checked - correct,
        "severity_accuracy": (
            round(correct / checked, 3)
            if checked
            else None
        ),
        "matches": matched,
    }

