import re


def search_keyword(
    document,
    keyword: str
):
    """
    Exact, case-insensitive keyword search
    across the original extracted document.

    Returns:
        - whether the keyword exists
        - exact count
        - pages containing the keyword
        - occurrences per page
    """

    keyword = keyword.strip()

    if not keyword:
        return {
            "found": False,
            "count": 0,
            "pages": [],
            "occurrences": {}
        }

    # Exact word matching.
    # Example:
    # Phonic matches Phonic and PHONIC
    # but not Phonically.
    pattern = re.compile(
        rf"\b{re.escape(keyword)}\b",
        re.IGNORECASE
    )

    total_count = 0
    pages = []
    occurrences = {}

    for page in document["pages"]:

        page_number = page["page_number"]
        text = page.get("text", "")

        matches = pattern.findall(text)

        count = len(matches)

        if count > 0:

            total_count += count

            pages.append(page_number)

            occurrences[
                page_number
            ] = count

    return {
        "found": total_count > 0,
        "count": total_count,
        "pages": pages,
        "occurrences": occurrences
    }