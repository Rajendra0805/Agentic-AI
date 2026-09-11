def get_document_metadata(document):

    pages = document.get(
        "pages",
        []
    )

    return {
        "page_count": len(pages),
        "document_name": document.get(
            "document_name"
        ),
        "file_type": "PDF"
    }