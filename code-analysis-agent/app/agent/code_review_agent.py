import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.models.code_review_models import (
    CodeReviewResult
)

from app.review.review_validation import (
    ReviewValidator
)

from app.services.tool_router import ToolRouter
from app.tools.tool_definitions import TOOLS


load_dotenv()


class CodeReviewAgent:

    def __init__(self, repository_path: str):

        self.tool_router = ToolRouter(
            repository_path
        )
        self.validator = ReviewValidator()

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

    def run(
        self,
        user_question: str
    ) -> CodeReviewResult:

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

        for iteration in range(
            max_iterations + 1
        ):

            print(
                f"\n[Review Agent] "
                f"Iteration {iteration + 1}"
            )

            is_final_turn = (
                iteration == max_iterations
            )

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
                            f"Review request:\n"
                            f"{user_question}\n\n"

                            "Repository evidence collected:\n"
                            f"{json.dumps(tool_observations, indent=2)}\n\n"

                            "Produce the final code review now.\n"
                            "Do not call tools.\n"
                            "Use only the evidence provided.\n"
                            "Do not invent repository facts."
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

                request_options[
                    "tool_choice"
                ] = "auto"

            response = (
                self.client
                .chat
                .completions
                .create(
                    **request_options
                )
            )

            assistant_message = (
                response
                .choices[0]
                .message
            )

            messages.append(
                assistant_message
            )

            tool_calls = (
                assistant_message.tool_calls
            )

            if not tool_calls:

                return self._parse_review(
                    assistant_message.content,
                    user_question
                )

            for tool_call in tool_calls:

                tool_name = (
                    tool_call
                    .function
                    .name
                )

                arguments_text = (
                    tool_call
                    .function
                    .arguments
                )

                try:

                    arguments = json.loads(
                        arguments_text
                    )

                except json.JSONDecodeError:

                    arguments = {}

                print(
                    f"[Review Agent] "
                    f"Tool requested: "
                    f"{tool_name}"
                )

                print(
                    f"[Review Agent] "
                    f"Arguments: "
                    f"{arguments}"
                )

                tool_call_count += 1

                if (
                    tool_call_count
                    > max_tool_calls
                ):

                    return self._fallback_result(
                        user_question,
                        "The agent reached the "
                        "maximum number of tool calls."
                    )

                try:

                    result = (
                        self.tool_router.execute(
                            tool_name,
                            arguments
                        )
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

                messages.append({
                    "role": "tool",
                    "tool_call_id":
                        tool_call.id,
                    "content":
                        tool_result
                })

        return self._fallback_result(
            user_question,
            "The agent could not produce "
            "a final review."
        )

    def _parse_review(
        self,
        content: str | None,
        user_question: str
    ) -> CodeReviewResult:

        if not content:

            return self._fallback_result(
                user_question,
                "The model returned an empty response."
            )

        try:

            data = json.loads(
                content
            )

            review = CodeReviewResult.model_validate(
                data
            )

            validated_review = (
                self.validator.validate(
                    review
                )
            )

            return validated_review

        except Exception as exc:

            print(
                "[Review Agent] "
                "Structured output parsing failed:"
            )

            print(str(exc))

            return self._fallback_result(
                user_question,
                content
            )

    def _fallback_result(
        self,
        user_question: str,
        message: str
    ) -> CodeReviewResult:

        return CodeReviewResult(
            repository="unknown",
            reviewed_scope=user_question,
            summary=message,
            findings=[]
        )

    def _system_prompt(self):

        return """
You are a senior .NET Code Review Agent.

Your responsibility is to review actual repository code
and identify meaningful engineering issues.

You must use repository evidence before reporting a finding.

==================================================
REVIEW CATEGORIES
==================================================

Review the following categories when relevant:

1. Security
2. Architecture
3. Performance
4. Maintainability
5. Reliability
6. Code Quality

Do not force findings for every category.

If a category has no evidence of an issue,
do not create a finding.

==================================================
TOOL SELECTION
==================================================

Use find_api_endpoints when investigating:

- ASP.NET Core controllers
- API endpoints
- HTTP routes
- endpoint structure

Use find_database_usage when investigating:

- DbContext
- Entity Framework Core
- SqlConnection
- Dapper
- database providers
- database access

Use find_dependencies when investigating:

- NuGet packages
- project references
- project dependencies

Use search_code when investigating:

- specific implementation details
- business logic
- authentication
- authorization
- SQL queries
- exception handling
- configuration
- secrets
- complex methods
- architecture implementation
- potential vulnerabilities

==================================================
EVIDENCE RULES
==================================================

1. Every finding MUST have repository evidence.

2. Never invent code.

3. Never assume a vulnerability exists without
   sufficient evidence.

4. If a problem is only possible rather than confirmed,
   describe it as a potential concern.

5. Include the exact file path.

6. Include line numbers when available.

7. Evidence must come from repository tools.

8. Do not use general programming knowledge as
   evidence for a repository-specific finding.

==================================================
SEVERITY RULES
==================================================

Critical:
Immediate severe security or production risk.

High:
Significant security, reliability, or architectural risk.

Medium:
Important engineering problem that should be addressed.

Low:
Minor issue or maintainability improvement.

Info:
Observation or recommendation that is not a defect.

Do not exaggerate severity.

==================================================
CONFIDENCE
==================================================

Confidence must be between 0 and 1.

Use:

0.90 - 1.00
Strong direct evidence.

0.75 - 0.89
Good evidence with minor uncertainty.

0.50 - 0.74
Potential issue requiring further investigation.

Below 0.50
Do not report as a confirmed finding.

==================================================
REVIEW PROCESS
==================================================

Follow this process:

1. Understand the review request.

2. Determine which review categories are relevant.

3. Select the minimum tools necessary.

4. Collect repository evidence.

5. Analyze the evidence.

6. If evidence is insufficient, search for
   additional evidence.

7. Do not repeat essentially identical searches.

8. Validate that each finding is actually supported.

9. Assign severity.

10. Assign confidence.

11. Produce the final review.

==================================================
IMPORTANT
==================================================

Do not produce findings simply because a best practice
exists.

A best practice becomes a finding only when the actual
repository code provides evidence that it is relevant.

Prefer:

3 strong findings

over:

15 generic findings.

You are READ-ONLY.

Never modify repository files.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use this structure:

{
  "repository": "repository name",
  "reviewed_scope": "scope reviewed",
  "summary": "overall review summary",
  "findings": [
    {
      "category": "Security",
      "severity": "High",
      "title": "Short finding title",
      "description": "Detailed explanation",
      "file_path": "path/to/file.cs",
      "start_line": 10,
      "end_line": 15,
      "evidence": "Actual repository evidence",
      "recommendation": "Practical recommendation",
      "confidence": 0.95
    }
  ]
}

If no significant issues are found:

"findings": []

Remember:

Evidence first.
Analysis second.
Finding third.
Recommendation fourth.
"""