
import re
from pathlib import Path

from app.documentation.documentation_models import (
    DocumentationResult,
)


class DocumentationValidator:
    """
    Validates generated documentation before it is saved.

    Checks:
    - Required document sections
    - Empty content
    - Source-file paths and repository boundaries
    - Potential secret exposure
    - Duplicate document types
    """

    REQUIRED_SECTIONS = {
        "README": ["purpose", "setup"],
        "ARCHITECTURE": ["architecture"],
        "API_REFERENCE": ["api"],
        "CONFIGURATION": ["configuration"],
    }

    # These patterns are a best-effort safety check, not a complete
    # secret scanner. Avoid printing matched secret values.
    SECRET_PATTERNS = [
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret)"
            r"\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{12,})"
        ),
        re.compile(
            r"(?i)\b(password|passwd|pwd)\b\s*[:=]\s*"
            r"['\"]([^'\"]{4,})['\"]"
        ),
        re.compile(
            r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"
        ),
        re.compile(
            r"(?i)\bgh[pousr]_[A-Za-z0-9]{30,}\b"
        ),
    ]

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

    def validate(self, result: DocumentationResult) -> dict:
        errors = []
        warnings = []
        seen_types = set()

        if not self.repository_path.is_dir():
            return {
                "is_valid": False,
                "errors": ["Repository directory does not exist."],
                "warnings": [],
            }

        if not result.generated_documents:
            errors.append("No documents were generated.")

        for document in result.generated_documents:
            document_type = str(document.document_type)

            if document_type in seen_types:
                errors.append(
                    f"Duplicate document type: {document_type}"
                )
            seen_types.add(document_type)

            if not document.title.strip():
                errors.append(
                    f"{document_type}: document title is empty."
                )

            if not document.summary.strip():
                warnings.append(
                    f"{document_type}: document summary is empty."
                )

            if not document.sections:
                errors.append(
                    f"{document_type}: no sections were generated."
                )

            combined_text = "\n".join(
                [
                    document.title,
                    document.summary,
                    *[
                        f"{section.title}\n{section.content}"
                        for section in document.sections
                    ],
                ]
            )

            # Check for potential secret exposure.
            for pattern in self.SECRET_PATTERNS:
                if pattern.search(combined_text):
                    errors.append(
                        f"{document_type}: potential secret exposure "
                        "detected. Review the generated content "
                        "without logging the matched value."
                    )
                    break

            # Validate required section topics.
            section_titles = " ".join(
                section.title.lower()
                for section in document.sections
            )

            required_topics = self.REQUIRED_SECTIONS.get(
                document_type, []
            )

            for topic in required_topics:
                if topic not in section_titles:
                    warnings.append(
                        f"{document_type}: no section title clearly "
                        f"references '{topic}'."
                    )

            # Validate source-file references.
            for section in document.sections:
                if not section.title.strip():
                    errors.append(
                        f"{document_type}: a section has an empty title."
                    )

                if not section.content.strip():
                    errors.append(
                        f"{document_type}: section "
                        f"'{section.title}' has empty content."
                    )

                for source in section.source_files:
                    path_error = self._validate_source_path(source)

                    if path_error:
                        warnings.append(
                            f"{document_type}, section "
                            f"'{section.title}': {path_error}"
                        )

        errors.extend(
            f"Agent warning: {warning}"
            for warning in result.warnings
        )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "document_count": len(result.generated_documents),
        }

    def _validate_source_path(self, source: str) -> str | None:
        """Check that a source reference points inside the repository."""

        if not source.strip():
            return "An empty source-file path was supplied."

        relative_path = Path(source)

        if relative_path.is_absolute():
            return "Absolute source-file paths are not allowed."

        try:
            resolved_path = (
                self.repository_path / relative_path
            ).resolve()

            resolved_path.relative_to(self.repository_path)
        except (ValueError, OSError, RuntimeError):
            return "Source path escapes the repository or is invalid."

        if not resolved_path.is_file():
            return f"Referenced source file does not exist: {source}"

        return None
