import json

from agent.llm import call_llm


QUERY_REWRITE_PROMPT = """
You are a query rewriting assistant.

Your job is to rewrite the user's latest
question into a standalone document-search
query.

Use the conversation history to resolve
references such as:

- it
- this
- that
- they
- those
- the above
- mentioned earlier
- that topic

Rules:

1. Preserve the user's intent.

2. Do not answer the question.

3. Do not add information that is not present
   in the conversation.

4. Return ONLY the rewritten query.

Examples:

Conversation:
User: What is Phonic?
Assistant: Phonic is related to sounds.

Latest question:
How many times is it mentioned?

Rewritten query:
Phonic

---

Conversation:
User: What does the document say about English?
Assistant: ...

Latest question:
Which pages mention it?

Rewritten query:
English

---

Latest question:
How many pages does the document have?

Rewritten query:
How many pages does the document have?
"""


def rewrite_query(
    question,
    conversation
):

    messages = [
        {
            "role": "system",
            "content": QUERY_REWRITE_PROMPT
        },
        {
            "role": "user",
            "content": json.dumps({
                "conversation": conversation,
                "latest_question": question
            })
        }
    ]

    response = call_llm(
        messages,
        tools=None
    )

    rewritten = (
        response
        .choices[0]
        .message
        .content
    )

    return rewritten.strip()