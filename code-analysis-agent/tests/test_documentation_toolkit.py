
from unittest.mock import Mock

from app.documentation.documentation_toolkit import (
    DocumentationToolkit,
)


def test_rejects_unapproved_tool(tmp_path):
    toolkit = DocumentationToolkit(str(tmp_path))

    result = toolkit.execute("delete_files", {})

    assert result["success"] is False
    assert "not allowed" in result["error"]


def test_rejects_arguments_for_no_argument_tool(tmp_path):
    toolkit = DocumentationToolkit(str(tmp_path))

    result = toolkit.execute(
        "find_project_files",
        {"unexpected": "value"},
    )

    assert result["success"] is False


def test_search_code_requires_query(tmp_path):
    toolkit = DocumentationToolkit(str(tmp_path))

    result = toolkit.execute("search_code", {})

    assert result["success"] is False
    assert "query" in result["error"]


def test_executes_approved_tool(tmp_path):
    toolkit = DocumentationToolkit(str(tmp_path))
    toolkit.tool_router.execute = Mock(
        return_value="Found project files"
    )

    result = toolkit.execute("find_project_files", {})

    assert result["success"] is True
    assert result["data"] == "Found project files"
    toolkit.tool_router.execute.assert_called_once_with(
        "find_project_files",
        {},
    )
