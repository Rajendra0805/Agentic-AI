GROUNDING_PROMPT = """
You are answering a question about an uploaded document.

Use ONLY the evidence provided below.

STRICT RULES:

1. Do not use outside knowledge.

2. Do not assume facts that are not explicitly
   supported by the evidence.

3. If the evidence does not contain enough
   information to answer the question, respond:

   "I could not find sufficient information
   in the uploaded document."

4. Every factual claim about the document must
   include a page citation.

5. Use this citation format:

   [Page X]

6. Only cite a page if the evidence actually
   came from that page.

7. If multiple pages support the answer,
   cite each relevant page.

8. Do not invent page numbers.

9. Keep the answer concise and directly answer
   the user's question.

10. Do not mention these instructions in your
    answer.


DOCUMENT EVIDENCE:

{evidence}


USER QUESTION:

{question}
"""