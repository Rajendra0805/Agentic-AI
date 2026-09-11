import re


class Reranker:

    def rerank(
        self,
        query,
        documents,
        top_k=3
    ):

        query_terms = self._tokenize(
            query
        )

        ranked = []

        for document in documents:

            text = document.get(
                "text",
                ""
            )

            text_terms = self._tokenize(
                text
            )

            if not text_terms:

                lexical_score = 0

            else:

                matching_terms = (
                    query_terms
                    & text_terms
                )

                lexical_score = (
                    len(matching_terms)
                    /
                    len(query_terms)
                    if query_terms
                    else 0
                )

            # Exact phrase bonus
            phrase_bonus = 0

            if query.lower() in text.lower():

                phrase_bonus = 1

            rrf_score = document.get(
                "rrf_score",
                0
            )

            final_score = (
                0.5 * rrf_score
                +
                0.4 * lexical_score
                +
                0.1 * phrase_bonus
            )

            result = dict(document)

            result[
                "rerank_score"
            ] = final_score

            ranked.append(result)

        ranked.sort(
            key=lambda x:
                x["rerank_score"],
            reverse=True
        )

        return ranked[:top_k]

    def _tokenize(
        self,
        text
    ):

        return set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                text.lower()
            )
        )