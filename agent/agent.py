import json

from agent.llm import ask_agent

from agent.tools import (
    search_document,
    get_document_stats,
    extract_section,
    find_keywords,
    find_dates,
    calculate
)


SYSTEM_PROMPT = """
You are a Document Analysis Agent.

You have access to two document tools.

TOOL 1: search_knowledge_base

Use this for semantic questions where the
user wants to understand or retrieve information
from the document.

Examples:
- What does the document say about security?
- How does authentication work?
- Explain the project architecture.
- What are the project risks?


TOOL 2: search_keyword

Use this for exact word or phrase questions.

Examples:
- Is Phonic present?
- How many times does Phonic appear?
- Where is English mentioned?
- How many occurrences of API are there?


IMPORTANT:

If the user asks for an exact count of a word
or phrase, ALWAYS use search_keyword.

Do NOT use semantic search to count occurrences.

If the user asks whether a specific word exists,
use search_keyword.

Do not invent information.

When answering document questions, include
page numbers when available.

Do not create fake citations.

Only cite pages returned by the document tools.
"""

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": (
                "Search the document for a keyword "
                "or phrase."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": (
                            "Keyword or phrase to search for."
                        )
                    }
                },
                "required": ["keyword"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_document_stats",
            "description": (
                "Get statistics about the document."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["document"],
                        "description": (
                            "The scope of the request. Always use document."
                        )
                    }
                },
                "required": ["scope"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "extract_section",
            "description": (
                "Find and extract a named section "
                "from the document."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "section_name": {
                        "type": "string",
                        "description": (
                            "Name of the section."
                        )
                    }
                },
                "required": ["section_name"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_keywords",
            "description": (
                "Search the document for multiple "
                "keywords."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": (
                            "List of keywords to search for."
                        )
                    }
                },
                "required": ["keywords"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_dates",
            "description": (
                "Find dates mentioned in the document."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["document"],
                        "description": (
                            "The scope of the request. Always use document."
                        )
                    }
                },
                "required": ["scope"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Perform basic mathematical calculations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Mathematical expression "
                            "such as 125 * 20 / 100."
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    }

]

def execute_tool(
    tool_name,
    arguments,
    document
):

    if tool_name == "search_document":

        return search_document(
            document,
            arguments["keyword"]
        )

    elif tool_name == "get_document_stats":

        return get_document_stats(
            document
        )

    elif tool_name == "extract_section":

        return extract_section(
            document,
            arguments["section_name"]
        )

    elif tool_name == "find_keywords":

        return find_keywords(
            document,
            arguments["keywords"]
        )

    elif tool_name == "find_dates":

        return find_dates(
            document
        )

    elif tool_name == "calculate":

        return calculate(
            arguments["expression"]
        )

    else:

        return {
            "error": f"Unknown tool: {tool_name}"
        }

def run_agent(document, user_question):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    max_iterations = 8

    for iteration in range(max_iterations):

        print(
            f"\n[Agent Iteration {iteration + 1}]"
        )

        response = ask_agent(
            messages,
            TOOLS
        )

        if not response.tool_calls:

            return response.content

        messages.append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in response.tool_calls
            ]
        })

        for tool_call in response.tool_calls:

            tool_name = tool_call.function.name

            try:

                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError:

                tool_result = {
                    "error": "Invalid tool arguments."
                }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

                continue

            print(
                f"[Tool] {tool_name}"
            )

            print(
                f"[Arguments] {arguments}"
            )

            tool_result = execute_tool(
                tool_name,
                arguments,
                document
            )

            print(
                f"[Tool Result] {tool_result}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

    return (
        "The agent reached the maximum number "
        "of processing steps."
    )