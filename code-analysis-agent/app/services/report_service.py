from app.models.analysis_models import AnalysisResult


def create_markdown_report(
    result: AnalysisResult
) -> str:

    lines = []

    lines.append(
        f"# Code Analysis Report: {result.repository}"
    )

    lines.append("")

    lines.append("## Architecture")

    lines.append(
        f"- Pattern: {result.architecture_pattern}"
    )

    lines.append(
        f"- Confidence: "
        f"{result.architecture_confidence:.0%}"
    )

    lines.append("")

    lines.append("## Summary")

    lines.append(result.summary)

    lines.append("")

    lines.append("## Projects")

    for project in result.projects:
        lines.append(f"- {project}")

    lines.append("")

    lines.append("## API Files")

    for api_file in result.api_files:
        lines.append(f"- {api_file}")

    lines.append("")

    lines.append("## Database Files")

    for database_file in result.database_files:
        lines.append(f"- {database_file}")

    lines.append("")

    lines.append("## Findings")

    for finding in result.findings:

        lines.append(
            f"### [{finding.severity}] "
            f"{finding.title}"
        )

        lines.append(
            finding.description
        )

        lines.append("")

        lines.append(
            f"**Recommendation:** "
            f"{finding.recommendation}"
        )

        lines.append("")

    return "\n".join(lines)