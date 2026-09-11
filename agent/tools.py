import re
from datetime import datetime
import unicodedata

def normalize_text(text):

    if not text:
        return ""

    # Normalize Unicode
    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Replace line breaks with spaces
    text = text.replace("\n", " ")

    # Collapse multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip().lower()

def normalize_for_search(text):

    if not text:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Remove whitespace completely
    text = re.sub(
        r"\s+",
        "",
        text
    )

    return text.lower()

def search_document(document, keyword):

    pages = document["pages"]

    normal_keyword = normalize_text(
        keyword
    )

    compact_keyword = normalize_for_search(
        keyword
    )

    results = []

    for page in pages:

        page_text = page["text"]

        normal_page = normalize_text(
            page_text
        )

        compact_page = normalize_for_search(
            page_text
        )

        normal_match = (
            normal_keyword in normal_page
        )

        compact_match = (
            compact_keyword in compact_page
        )

        if normal_match or compact_match:

            results.append({
                "page_number": page["page_number"],
                "match": keyword
            })

    return {
        "keyword": keyword,
        "found": len(results) > 0,
        "match_count": len(results),
        "matches": results[:20]
    }   


def get_document_stats(document):

    text = document["full_text"]

    return {
        "file_name": document["file_name"],
        "file_type": document["file_type"],
        "page_count": document["page_count"],
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
        "paragraphs": len(
            [
                p
                for p in text.split("\n\n")
                if p.strip()
            ]
        )
    }


def extract_section(document, section_name):

    if isinstance(document, str):
        text = document
    elif isinstance(document, dict):
        text = document.get("full_text", "")

        if isinstance(text, dict):
            text = "\n".join(
                value
                for value in text.values()
                if isinstance(value, str)
            )
    else:
        text = ""

    lines = text.splitlines()

    start_index = None

    for i, line in enumerate(lines):

        if section_name.lower() in line.lower():

            start_index = i
            break

    if start_index is None:

        return {
            "found": False,
            "section": section_name,
            "content": ""
        }

    section_lines = lines[
        start_index:start_index + 50
    ]

    return {
        "found": True,
        "section": section_name,
        "content": "\n".join(section_lines)
    }


def find_keywords(document, keywords):

    results = {}

    for keyword in keywords:

        result = search_document(
            document,
            keyword
        )

        results[keyword] = {
            "found": result["found"],
            "match_count": result["match_count"],
            "matches": result["matches"]
        }

    return results


def find_dates(document):

    text = document["full_text"]

    patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        r"\b\d{1,2}-\d{1,2}-\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b"
    ]

    dates = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        dates.extend(matches)

    dates = list(dict.fromkeys(dates))

    return {
        "found": len(dates) > 0,
        "count": len(dates),
        "dates": dates
    }


def calculate(expression):
    """
    Perform basic arithmetic.

    Only allows numbers and arithmetic operators.
    """

    if not re.fullmatch(
        r"[0-9+\-*/().\s]+",
        expression
    ):
        return {
            "error": "Invalid mathematical expression."
        }

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return {
            "expression": expression,
            "result": result
        }

    except Exception as error:

        return {
            "error": str(error)
        }