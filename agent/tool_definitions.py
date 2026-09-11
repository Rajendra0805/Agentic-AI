from agent.keyword_tool_definition import (
    SEARCH_KEYWORD_TOOL
)

SEARCH_KNOWLEDGE_BASE_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": (
            "Search the uploaded document using "
            "semantic search. Use this tool when "
            "the user asks about information that "
            "may exist inside the document."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The information to search "
                        "for in the document."
                    )
                },
                "top_k": {
                    "type": "integer",
                    "description": (
                        "Number of relevant document "
                        "chunks to retrieve."
                    ),
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

TOOLS = [
    SEARCH_KNOWLEDGE_BASE_TOOL,
    SEARCH_KEYWORD_TOOL
]