from pathlib import Path
from pypdf import PdfReader


def load_document(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() == ".pdf":
        return load_pdf(path)

    elif path.suffix.lower() == ".txt":
        return load_txt(path)

    else:
        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )


def load_pdf(path):

    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    full_text = "\n".join(
        page["text"]
        for page in pages
    )

    return {
        "file_name": path.name,
        "file_type": "pdf",
        "page_count": len(pages),
        "pages": pages,
        "full_text": full_text
    }


def load_txt(path):

    text = path.read_text(
        encoding="utf-8"
    )

    return {
        "file_name": path.name,
        "file_type": "txt",
        "page_count": None,
        "pages": [],
        "full_text": text
    }