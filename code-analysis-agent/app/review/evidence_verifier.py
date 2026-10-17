
from pathlib import Path

from app.models.code_review_models import (
    CodeReviewResult,
)


class EvidenceVerifier:
    """Verify finding locations and quoted source evidence."""

    def __init__(self, repository_path: str):
        self.repository_path = Path(
            repository_path
        ).resolve()

    def verify(
        self,
        review: CodeReviewResult,
    ) -> dict:
        results = []

        for finding in review.findings:
            result = self._verify_finding(finding)
            results.append(result)

        verified_count = sum(
            1 for result in results
            if result["status"] == "verified"
        )

        return {
            "total_findings": len(results),
            "verified_count": verified_count,
            "unverified_count": len(results) - verified_count,
            "results": results,
        }

    def _verify_finding(self, finding) -> dict:
        relative_path = Path(finding.file_path)

        # Prevent absolute paths and directory traversal
        # from accessing files outside the repository.
        if relative_path.is_absolute():
            return self._result(
                finding,
                "unverified",
                "Absolute file paths are not allowed.",
            )

        try:
            file_path = (
                self.repository_path / relative_path
            ).resolve()

            file_path.relative_to(self.repository_path)

        except (ValueError, OSError):
            return self._result(
                finding,
                "unverified",
                "File path escapes the repository or is invalid.",
            )

        if not file_path.is_file():
            return self._result(
                finding,
                "unverified",
                "Referenced file does not exist.",
            )

        try:
            source_lines = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

        except OSError as exc:
            return self._result(
                finding,
                "unverified",
                f"Could not read source file: {exc}",
            )

        start_line = finding.start_line
        end_line = finding.end_line

        if start_line is not None:
            if start_line < 1 or start_line > len(source_lines):
                return self._result(
                    finding,
                    "unverified",
                    "Start line is outside the source file.",
                )

        if end_line is not None:
            if end_line < 1 or end_line > len(source_lines):
                return self._result(
                    finding,
                    "unverified",
                    "End line is outside the source file.",
                )

        if (
            start_line is not None
            and end_line is not None
            and end_line < start_line
        ):
            return self._result(
                finding,
                "unverified",
                "End line precedes start line.",
            )

        if start_line is not None:
            effective_end = end_line or start_line
            excerpt = "\n".join(
                source_lines[start_line - 1:effective_end]
            )
        else:
            excerpt = "\n".join(source_lines)

        evidence = finding.evidence.strip()

        if not evidence:
            return self._result(
                finding,
                "unverified",
                "Finding has no evidence.",
            )

        # Exact substring matching is deliberately conservative.
        # A mismatch may be due to formatting or paraphrasing,
        # not necessarily a false finding.
        if evidence not in excerpt:
            return self._result(
                finding,
                "unverified",
                "Quoted evidence was not found in the cited source range.",
            )

        return self._result(
            finding,
            "verified",
            "File, line range, and quoted evidence were verified.",
        )

    @staticmethod
    def _result(
        finding,
        status: str,
        reason: str,
    ) -> dict:
        return {
            "category": str(finding.category),
            "title": finding.title,
            "file_path": finding.file_path,
            "start_line": finding.start_line,
            "end_line": finding.end_line,
            "status": status,
            "reason": reason,
        }
