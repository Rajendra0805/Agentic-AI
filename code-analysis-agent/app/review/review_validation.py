from app.models.code_review_models import (
    CodeReviewResult,
    ReviewFinding
)


ALLOWED_CATEGORIES = {
    "Security",
    "Architecture",
    "Performance",
    "Maintainability",
    "Reliability",
    "Code Quality"
}


ALLOWED_SEVERITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
    "Info"
}

class ReviewValidator:

    def validate(
        self,
        review: CodeReviewResult
    ) -> CodeReviewResult:

        valid_findings = []

        for finding in review.findings:

            if not self._is_valid_finding(
                finding
            ):
                continue

            valid_findings.append(
                finding
            )

        valid_findings = (
            self._remove_duplicates(
                valid_findings
            )
        )

        return CodeReviewResult(
            repository=review.repository,
            reviewed_scope=review.reviewed_scope,
            summary=review.summary,
            findings=valid_findings
        )

    def _is_valid_finding(
        self,
        finding: ReviewFinding
    ) -> bool:

        if finding.category not in ALLOWED_CATEGORIES:
            return False

        if finding.severity not in ALLOWED_SEVERITIES:
            return False

        if not finding.file_path.strip():
            return False

        if not finding.evidence.strip():
            return False

        if not finding.description.strip():
            return False

        if not finding.recommendation.strip():
            return False

        if finding.confidence < 0:
            return False

        if finding.confidence > 1:
            return False

        return True
    

    def _remove_duplicates(
        self,
        findings: list[ReviewFinding]
    ) -> list[ReviewFinding]:

        unique_findings = []

        seen = set()

        for finding in findings:

            key = (
                finding.category.lower(),
                finding.file_path.lower(),
                finding.title.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            unique_findings.append(
                finding
            )

        return unique_findings