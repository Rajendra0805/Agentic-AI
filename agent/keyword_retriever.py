import re


class KeywordRetriever:

    def __init__(self, document):

        self.document = document

    def search(
        self,
        query,
        max_results=10
    ):

        query = query.strip()

        if not query:
            return []

        pattern = re.compile(
            re.escape(query),
            re.IGNORECASE
        )

        results = []

        for page in self.document.get(
            "pages",
            []
        ):

            page_number = page.get(
                "page_number"
            )

            text = page.get(
                "text",
                ""
            )

            matches = pattern.findall(
                text
            )

            if not matches:
                continue

            results.append({
                "page_number": page_number,
                "text": text,
                "keyword_matches": len(matches)
            })

        results.sort(
            key=lambda x:
                x["keyword_matches"],
            reverse=True
        )

        return results[:max_results]