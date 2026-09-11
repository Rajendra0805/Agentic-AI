import json

from agent.llm import call_llm
from agent.keyword_tool import search_keyword
from agent.tools_rag import search_knowledge_base
from agent.evidence import EvidenceBuilder
from agent.prompts import GROUNDING_PROMPT
from agent.memory import ConversationMemory

from agent.query_rewriter import (
    rewrite_query
)

from agent.tool_definitions import (
    SEARCH_KNOWLEDGE_BASE_TOOL
)

from agent.keyword_tool_definition import (
    SEARCH_KEYWORD_TOOL
)

from agent.document_metadata import (
    get_document_metadata
)

from agent.metadata_tool_definition import (
    GET_DOCUMENT_METADATA_TOOL
)


SYSTEM_PROMPT = """
You are a reliable Document Analysis Agent.

You have three document tools.

1. search_keyword

Use for exact word or phrase questions.

Examples:
- Is Phonic present?
- How many times does Phonic appear?
- Which pages contain English?


2. search_knowledge_base

Use for semantic/document-content questions.

Examples:
- What is Phonic?
- Explain authentication.
- What does the document say about security?


3. get_document_metadata

Use for document metadata questions.

Examples:
- How many pages does the document have?
- What is the document name?
- What type of document is this?


IMPORTANT RULES:

1. Exact counting must use search_keyword.

2. Semantic document questions must use
   search_knowledge_base.

3. Questions about page count or document
   metadata must use get_document_metadata.

4. Never guess the number of pages.

5. Never invent document information.

6. If a tool returns no information,
   clearly say that the information was
   not found.

7. Include page numbers when they are
   available.

8. Do not create fake citations.

9. CONVERSATION CONTEXT

The user may ask follow-up questions.

Examples:

User: What is Phonic?
User: How many times is it mentioned?

In the second question, "it" refers to Phonic.

Use the conversation history to resolve
references before selecting a document tool.

Do not treat a follow-up question as an
independent question when its meaning depends
on previous messages.
"""


class DocumentAgent:

    def __init__(
        self,
        document,
        rag_engine
    ):

        self.document = document
        self.rag_engine = rag_engine
        self.evidence_builder = (
            EvidenceBuilder()
        )
        self.memory = ConversationMemory(
            max_messages=10
        )
        self.last_trace = {
            "rewritten_question": "",
            "tools": [],
            "evidence": []
        }

    def run(
        self,
        user_question
    ):
        self.last_trace = {
            "rewritten_question": "",
            "tools": [],
            "evidence": []
        }

        conversation = (
            self.memory.get_messages()
        )

        rewritten_question = rewrite_query(
            user_question,
            conversation
        )
        self.last_trace["rewritten_question"] = (
            rewritten_question
        )

        agent_question = f"""
        Original user question:

        {user_question}

        Resolved document query:

        {rewritten_question}

        Use the resolved query to select the
        appropriate document tool.
        """
        print(
            "\n[Agent] Original question:",
            user_question
        )

        print(
            "[Agent] Rewritten question:",
            rewritten_question
        )
        self.memory.add_user_message(
            user_question
        )
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
        messages.extend(
            self.memory.get_messages()
        )
        messages.append({
            "role": "user",
            "content": agent_question
        })

        tools = [
            SEARCH_KNOWLEDGE_BASE_TOOL,
            SEARCH_KEYWORD_TOOL,
            GET_DOCUMENT_METADATA_TOOL
        ]

        print(
            "\n[Agent] Sending question to Groq..."
        )

        # ==================================================
        # STEP 1 - Ask Groq to select the appropriate tool
        # ==================================================

        response = call_llm(
            messages,
            tools=tools
        )

        assistant_message = (
            response.choices[0].message
        )

        print(
            "\n[Agent] Tool calls:",
            assistant_message.tool_calls
        )

        # ==================================================
        # No tool required
        # ==================================================

        if not assistant_message.tool_calls:

            print(
                "[Agent] No tool was called."
            )

            return (
                assistant_message.content
                or "I could not generate an answer."
            )

        # ==================================================
        # STEP 2 - Add assistant tool-call message
        # ==================================================

        messages.append(
            assistant_message
        )

        # Track whether semantic RAG was used
        knowledge_base_used = False

        knowledge_base_result = None

        # ==================================================
        # STEP 3 - Execute tools
        # ==================================================

        for tool_call in (
            assistant_message.tool_calls
        ):

            tool_name = (
                tool_call.function.name
            )

            self.last_trace["tools"].append(
                tool_name
            )

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"\n[Agent] Calling tool: "
                f"{tool_name}"
            )

            print(
                f"[Agent] Arguments: "
                f"{arguments}"
            )

            # ----------------------------------------------
            # Exact keyword search
            # ----------------------------------------------

            if tool_name == "search_keyword":

                result = search_keyword(
                    self.document,
                    arguments["keyword"]
                )

            # ----------------------------------------------
            # Semantic RAG
            # ----------------------------------------------

            elif (
                tool_name
                == "search_knowledge_base"
            ):

                knowledge_base_used = True

                result = search_knowledge_base(
                    self.rag_engine,
                    arguments["query"],
                    arguments.get(
                        "top_k",
                        3
                    )
                )

                knowledge_base_result = result

            # ----------------------------------------------
            # Metadata
            # ----------------------------------------------

            elif (
                tool_name
                == "get_document_metadata"
            ):

                result = get_document_metadata(
                    self.document
                )

            # ----------------------------------------------
            # Unknown tool
            # ----------------------------------------------

            else:

                result = {
                    "error":
                    f"Unknown tool: {tool_name}"
                }

            print(
                f"[Agent] Tool result: "
                f"{result}"
            )

            # ----------------------------------------------
            # Add tool result to conversation
            # ----------------------------------------------

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result
                )
            })

        # ==================================================
        # STEP 4 - Build grounding context
        # ==================================================

        if knowledge_base_used:

            print(
                "\n[Agent] Building document evidence..."
            )

            evidence_items = (
                knowledge_base_result.get(
                    "evidence",
                    []
                )
            )
            self.last_trace["evidence"] = (
                evidence_items
            )

            if not evidence_items:

                print(
                    "[Agent] No evidence found."
                )

                return (
                    "I could not find sufficient "
                    "information in the uploaded "
                    "document."
                )

            evidence_text = (
                self.evidence_builder.build(
                    evidence_items
                )
            )

            print(
                "\n[Agent] Evidence:\n"
                + evidence_text
            )

            # ==============================================
            # Add explicit grounding instruction
            # ==============================================

            grounding_prompt = (
                GROUNDING_PROMPT.format(
                    evidence=evidence_text,
                    question=user_question
                )
            )

            messages.append({
                "role": "user",
                "content": grounding_prompt
            })

        # ==================================================
        # STEP 5 - Ask Groq for final answer
        # ==================================================

        print(
            "\n[Agent] Sending tool result "
            "back to Groq..."
        )

        final_response = call_llm(
            messages,
            tools=None
        )

        final_message = (
            final_response
            .choices[0]
            .message
        )

        print(
            "\n[Agent] Final response:",
            final_message.content
        )

        final_answer = (
            final_message.content
            or "I could not generate an answer."
        )

        self.memory.add_assistant_message(
            final_answer
        )

        return final_answer