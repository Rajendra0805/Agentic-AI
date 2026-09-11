class EvidenceBuilder:

    def build(
        self,
        results,
        max_chars_per_chunk=2500
    ):

        evidence = []

        for index, result in enumerate(
            results,
            start=1
        ):

            page = result.get(
                "page_number"
            )

            text = result.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            # Limit very large chunks
            text = text[
                :max_chars_per_chunk
            ]

            evidence.append(
                f"[Evidence {index} | Page {page}]\n"
                f"{text}"
            )

        return "\n\n".join(
            evidence
        )