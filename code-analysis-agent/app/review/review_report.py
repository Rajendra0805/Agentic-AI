
from datetime import datetime, timezone
from pathlib import Path

from app.models.code_review_models import CodeReviewResult


class ReviewReportGenerator:

    def generate(
        self,
        review: CodeReviewResult
    ) -> str:
        """Convert a validated review into Markdown."""

        findings = review.findings

        severity_order = {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
            "Low": 3,
            "Info": 4,
        }

        findings = sorted(
            findings,
            key=lambda finding: severity_order.get(
                str(finding.severity), 99
            )
        )

        counts = {
            severity: sum(
                1 for finding in findings
                if str(finding.severity) == severity
            )
            for severity in severity_order
        }

        lines = [
            "# Code Review Report",
            "",
            f"**Repository:** {review.repository}",
            f"**Reviewed scope:** {review.reviewed_scope}",
            (
                "**Generated at (UTC):** "
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            "",
            "## Executive Summary",
            "",
            review.summary,
            "",
            "## Findings Summary",
            "",
            f"- **Total findings:** {len(findings)}",
        ]

        for severity, count in counts.items():
            lines.append(f"- **{severity}:** {count}")

        lines.extend(["", "## Detailed Findings", ""])

        if not findings:
            lines.append("No findings were reported.")
        else:
            for number, finding in enumerate(findings, start=1):
                location = finding.file_path

                if finding.start_line is not None:
                    location += f":{finding.start_line}"

                    if finding.end_line is not None:
                        location += f"-{finding.end_line}"

                lines.extend([
                    f"### {number}. [{finding.severity}] {finding.title}",
                    "",
                    f"- **Category:** {finding.category}",
                    f"- **Location:** `{location}`",
                    f"- **Confidence:** {finding.confidence:.0%}",
                    "",
                    "**Description**",
                    "",
                    finding.description,
                    "",
                    "**Evidence**",
                    "",
                    "> " + finding.evidence.replace("\n", "\n> "),
                    "",
                    "**Recommendation**",
                    "",
                    finding.recommendation,
                    "",
                    "---",
                    "",
                ])

        lines.extend([
            "## Review Limitations",
            "",
            (
                "This report reflects the files and evidence available "
                "to the agent. Findings require developer verification; "
                "absence of findings does not prove the code is secure."
            ),
            "",
        ])

        return "\n".join(lines)

    def save(
        self,
        report: str,
        output_path: str
    ) -> str:
        """Save the report and return its resolved path."""

        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")

        return str(path)
