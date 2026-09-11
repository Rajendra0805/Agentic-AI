def build_rag_prompt(
    question,
    retrieved_chunks
):

    context_parts = []

    for chunk in retrieved_chunks:

        context_parts.append(
            f"""
Page {chunk['page_number']}:

{chunk['text']}
"""
        )

    context = "\n".join(
        context_parts
    )

    return f"""
You are a document analysis assistant.

Answer the user's question using only
the provided document context.

If the answer cannot be found in the
context, say that the information was
not found in the retrieved document
content.

Do not invent information.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}
"""