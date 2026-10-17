
from app.models.code_review_models import (
    CodeReviewResult,
    ReviewFinding,
)
from app.review.review_evaluator import (
    ExpectedFinding,
    ReviewEvaluator,
)


def make_finding(
    category: str,
    title: str,
    file_path: str,
    description: str,
) -> ReviewFinding:
    return ReviewFinding(
        category=category,
        severity="High",
        title=title,
        description=description,
        file_path=file_path,
        start_line=10,
        end_line=12,
        evidence="Example evidence from the source code",
        recommendation="Replace the problematic implementation.",
        confidence=0.95,
    )


def test_perfect_review():
    review = CodeReviewResult(
        repository="sample-repository",
        reviewed_scope="Full repository",
        summary="Two issues detected.",
        findings=[
            make_finding(
                "Security",
                "Hard-coded password",
                "CustomerRepository.cs",
                "A hard-coded password is present.",
            ),
            make_finding(
                "Reliability",
                "Possible null reference",
                "CustomerService.cs",
                "A null value may cause an exception.",
            ),
        ],
    )

    expected = [
        ExpectedFinding(
            "Security",
            "CustomerRepository.cs",
            "password",
        ),
        ExpectedFinding(
            "Reliability",
            "CustomerService.cs",
            "null",
        ),
    ]

    result = ReviewEvaluator().evaluate(review, expected)

    assert result["true_positives"] == 2
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1_score"] == 1.0


def test_missing_finding():
    review = CodeReviewResult(
        repository="sample-repository",
        reviewed_scope="Full repository",
        summary="One issue detected.",
        findings=[
            make_finding(
                "Security",
                "Hard-coded password",
                "CustomerRepository.cs",
                "A hard-coded password is present.",
            )
        ],
    )

    expected = [
        ExpectedFinding(
            "Security",
            "CustomerRepository.cs",
            "password",
        ),
        ExpectedFinding(
            "Reliability",
            "CustomerService.cs",
            "null",
        ),
    ]

    result = ReviewEvaluator().evaluate(review, expected)

    assert result["true_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["recall"] == 0.5


def test_unexpected_finding_counts_as_false_positive():
    review = CodeReviewResult(
        repository="sample-repository",
        reviewed_scope="Full repository",
        summary="One issue detected.",
        findings=[
            make_finding(
                "Code Quality",
                "Poor variable naming",
                "CustomerCalculator.cs",
                "The variable name could be more descriptive.",
            )
        ],
    )

    expected = [
        ExpectedFinding(
            "Security",
            "CustomerRepository.cs",
            "password",
        )
    ]

    result = ReviewEvaluator().evaluate(review, expected)

    assert result["true_positives"] == 0
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
