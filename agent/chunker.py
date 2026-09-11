def chunk_document(
    document,
    chunk_size=800,
    chunk_overlap=150
):
    """
    Split document pages into overlapping chunks.

    Each chunk retains page metadata.
    """

    chunks = []

    chunk_id = 0

    for page in document["pages"]:

        page_number = page["page_number"]

        text = page["text"].strip()

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "chunk_id": chunk_id,
                    "page_number": page_number,
                    "text": chunk_text
                })

                chunk_id += 1

            start += (
                chunk_size -
                chunk_overlap
            )

    return chunks