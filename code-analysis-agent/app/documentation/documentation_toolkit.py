
import json
from pathlib import Path
from typing import Any

from app.services.tool_router import ToolRouter


class DocumentationToolkit:
    """
    Read-only repository inspection toolkit for the Documentation Agent.

    Reuses existing Code Analysis Agent tools instead of duplicating
    repository inspection logic.
    """

    ALLOWED_TOOLS = {
        "list_files",
        "find_project_files",
        "find_api_endpoints",
        "find_database_usage",
        "find_dependencies",
        "search_code",
    }

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.is_dir():
            raise ValueError(
                f"Repository directory not found: "
                f"{self.repository_path}"
            )

        self.tool_router = ToolRouter(
            repository_path=str(self.repository_path)
        )

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute one approved repository-inspection tool.

        Arguments are dictionaries, matching the existing router's
        expected interface. Errors are returned without hiding them.
        """

        if tool_name not in self.ALLOWED_TOOLS:
            return {
                "success": False,
                "tool": tool_name,
                "error": "Tool is not allowed for documentation.",
            }

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            return {
                "success": False,
                "tool": tool_name,
                "error": "Tool arguments must be a dictionary.",
            }

        if tool_name != "search_code" and arguments:
            return {
                "success": False,
                "tool": tool_name,
                "error": (
                    "This tool does not accept arguments "
                    "through the documentation toolkit."
                ),
            }

        if tool_name == "search_code":
            query = arguments.get("query")

            if not isinstance(query, str) or not query.strip():
                return {
                    "success": False,
                    "tool": tool_name,
                    "error": "search_code requires a non-empty query.",
                }

            arguments = {"query": query.strip()}

        try:
            result = self.tool_router.execute(
                tool_name,
                arguments,
            )

            # Normalize the result so it can be passed to the LLM.
            if isinstance(result, str):
                normalized_result: Any = result
            else:
                normalized_result = result

            # Ensure the result can safely be serialized for inspection.
            json.dumps(normalized_result, ensure_ascii=False)

            return {
                "success": True,
                "tool": tool_name,
                "data": normalized_result,
            }

        except (Exception) as exc:
            return {
                "success": False,
                "tool": tool_name,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }

    def inspect_repository(self) -> dict[str, Any]:
        """
        Gather an initial repository overview for documentation.

        Each tool is executed independently so one failure does not
        prevent the remaining inspection steps.
        """

        inspection_plan = [
            ("list_files", {}),
            ("find_project_files", {}),
            ("find_api_endpoints", {}),
            ("find_database_usage", {}),
            ("find_dependencies", {}),
        ]

        results = {}

        for tool_name, arguments in inspection_plan:
            results[tool_name] = self.execute(
                tool_name,
                arguments,
            )

        successful = sum(
            1 for result in results.values()
            if result["success"]
        )

        return {
            "repository": str(self.repository_path),
            "tools_attempted": len(inspection_plan),
            "tools_succeeded": successful,
            "tools_failed": len(inspection_plan) - successful,
            "inspection_results": results,
        }

    def search_code(self, query: str) -> dict[str, Any]:
        """Search the repository for evidence about a topic."""

        return self.execute(
            "search_code",
            {"query": query},
        )
