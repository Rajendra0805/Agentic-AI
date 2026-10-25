
from app.documentation.documentation_models import (
    DocumentationResult,
    GeneratedDocument,
    DocumentationSection,
)
from app.documentation.documentation_validator import (
    DocumentationValidator,
)


def make_result():
    return DocumentationResult(
        repository="sample-repository",
        generated_documents=[
            GeneratedDocument(
                document_type="README",
                title="Project README",
                summary="Overview of the project.",
                sections=[
                    DocumentationSection(
                        title="Purpose",
                        content="This project manages customers.",
                    ),
                    DocumentationSection(
                        title="Setup",
                        content="Install the required dependencies.",
                    ),
                ],
            )
        ],
    )


def test_valid_documentation_passes(tmp_path):
    validator = DocumentationValidator(str(tmp_path))

    result = validator.validate(make_result())

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_empty_sections_fail(tmp_path):
    data = make_result()
    data.generated_documents[0].sections = []

    validator = DocumentationValidator(str(tmp_path))
    result = validator.validate(data)

    assert result["is_valid"] is False
    assert any("no sections" in error for error in result["errors"])


def test_secret_exposure_fails(tmp_path):
    data = make_result()
    data.generated_documents[0].sections[0].content = (
        "api_key = 'abcDEF123456789XYZ'"
    )

    validator = DocumentationValidator(str(tmp_path))
    result = validator.validate(data)

    assert result["is_valid"] is False
    assert any(
        "secret exposure" in error for error in result["errors"]
    )


def test_missing_source_file_warns(tmp_path):
    data = make_result()
    data.generated_documents[0].sections[0].source_files = [
        "missing.cs"
    ]

    validator = DocumentationValidator(str(tmp_path))
    result = validator.validate(data)

    assert result["is_valid"] is True
    assert any(
        "does not exist" in warning
        for warning in result["warnings"]
    )
