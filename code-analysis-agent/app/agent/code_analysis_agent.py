import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.services.tool_router import ToolRouter
from app.tools.tool_definitions import TOOLS

load_dotenv()


class CodeAnalysisAgent:

    def __init__(self, repository_path: str):

        self.tool_router = ToolRouter(repository_path)

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
            # "llama-3.3-70b-versatile"
        )

    def run(self, user_question: str):

        messages = [
            {
                "role": "system",
                "content": self._system_prompt()
            },
            {
                "role": "user",
                "content": user_question
            }
        ]

        max_iterations = 8
        max_tool_calls = 10

        tool_call_count = 0
        tool_observations = []

        # Reserve one extra model turn to synthesize a final answer after
        # the last permitted round of tool calls.
        for iteration in range(max_iterations + 1):

            print(
                f"\n[Agent] Iteration {iteration + 1}"
            )

            is_final_turn = iteration == max_iterations

            request_messages = messages
            if is_final_turn:
                request_messages = [
                    {
                        "role": "system",
                        "content": self._system_prompt()
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {user_question}\n\n"
                            "Repository tool results collected so far:\n"
                            f"{json.dumps(tool_observations, indent=2)}\n\n"
                            "Answer the question now using only these results. "
                            "Do not call tools. If the results do not answer it, "
                            "state what evidence is missing."
                        )
                    }
                ]

            request_options = {
                "model": self.model,
                "messages": request_messages,
                "temperature": 0
            }

            if not is_final_turn:
                request_options["tools"] = TOOLS
                request_options["tool_choice"] = "auto"

            response = self.client.chat.completions.create(
                **request_options
            )

            assistant_message = response.choices[0].message

            messages.append(assistant_message)

            tool_calls = assistant_message.tool_calls

            if not tool_calls:
                return assistant_message.content

            for tool_call in tool_calls:

                tool_name = tool_call.function.name

                arguments_text = (
                    tool_call.function.arguments
                )

                try:
                    arguments = json.loads(
                        arguments_text
                    )
                except json.JSONDecodeError:
                    arguments = {}

                print(
                    f"[Agent] Tool requested: "
                    f"{tool_name}"
                )

                print(
                    f"[Agent] Arguments: "
                    f"{arguments}"
                )

                try:
                    tool_call_count += 1

                    if tool_call_count > max_tool_calls:
                        return (
                        "The agent reached the maximum number "
                        "of tool calls. Please refine the question."
                        )
                    result = self.tool_router.execute(
                        tool_name,
                        arguments
                    )

                    tool_result = json.dumps(
                        result,
                        indent=2
                    )

                except Exception as exc:

                    tool_result = json.dumps({
                        "error": str(exc)
                    })

                tool_observations.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "output": tool_result
                })

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    }
                )

        return "The agent could not produce a final answer."

    def _system_prompt(self):

        return """
You are a senior .NET code analysis agent.

You answer questions about a repository using
deterministic repository tools and semantic code search.

TOOL SELECTION:

- For project/file counts:
  use find_project_files or list_files.

- For API endpoint questions:
  use find_api_endpoints.

- For database technology/configuration questions:
  use find_database_usage.

- For dependency questions:
  use find_dependencies.

- For implementation details or semantic questions:
  use search_code.

IMPORTANT:

1. Use the minimum number of tools necessary.

2. Do not call multiple tools when one tool provides
   sufficient evidence.

3. Do not repeat a search with essentially the same query.

4. After obtaining sufficient evidence, stop using tools
   and answer the user.

5. Never invent repository facts.

6. Base your answer on actual tool results.

7. Include file names and line numbers when available.

8. If the available evidence is insufficient, clearly
   state that.

9. You are read-only.

10. Never modify repository files.

Your primary objective is to answer the user's question
accurately and efficiently.
"""