from app.tools.repository_tools import RepositoryTools
from app.rag.code_rag import CodeRAG


class ToolRouter:

    def __init__(self, repository_path: str):

        self.tools = RepositoryTools(
            repository_path
        )

        self.code_rag = CodeRAG(
            repository_path
        )

        print("[Tool Router] Building code index...")

        self.code_rag.build_index()

    def execute(
        self,
        tool_name: str,
        arguments: dict
    ):

        print(
            f"[Tool Router] Executing: "
            f"{tool_name}"
        )
        if arguments is None:
            arguments = {}

        if tool_name == "list_files":
            return self.tools.list_files()

        if tool_name == "find_project_files":
            return self.tools.find_project_files()

        if tool_name == "find_api_endpoints":
            return self.tools.find_api_endpoints()

        if tool_name == "find_database_usage":
            return self.tools.find_database_usage()

        if tool_name == "find_dependencies":
            return self.tools.find_dependencies()

        if tool_name == "search_code":

            query = arguments.get("query")

            if not query:
                raise ValueError(
                    "search_code requires a query."
                )

            return self.code_rag.search(
                query=query,
                top_k=5
            )

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )