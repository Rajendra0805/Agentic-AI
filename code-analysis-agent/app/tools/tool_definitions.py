TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List relevant source-code files in the repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_project_files",
            "description": (
                "Find .NET solution and project files "
                "such as .sln and .csproj."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_api_endpoints",
            "description": (
                "Find ASP.NET Core API controller files "
                "and HTTP endpoint attributes."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_database_usage",
            "description": (
                "Find database access technologies and patterns "
                "such as Entity Framework Core, DbContext, "
                "SqlConnection, Dapper and database providers."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_dependencies",
            "description": (
                "Find project references and NuGet package "
                "dependencies from .csproj files."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": (
                "Search the repository source code semantically. "
                "Use this when you need to locate or understand "
                "specific implementation details that are not "
                "directly answered by deterministic repository tools."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Natural-language description of "
                            "the code or functionality to find."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    }
]