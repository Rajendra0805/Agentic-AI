from app.models.code_review_models import (
    CodeReviewResult
)


def main():

    review_data = {
        "repository": "sample-repository",

        "reviewed_scope":
            "CustomerController.cs",

        "summary":
            "One architecture issue was identified.",

        "findings": [
            {
                "category": "Architecture",

                "severity": "Medium",

                "title":
                    "Business logic in controller",

                "description":
                    "Business logic appears to be implemented "
                    "inside the controller.",

                "file_path":
                    "Customer.Api/Controllers/CustomerController.cs",

                "start_line": 15,

                "end_line": 25,

                "evidence":
                    "The controller contains business logic "
                    "inside the endpoint method.",

                "recommendation":
                    "Move the business logic into the "
                    "application/service layer.",

                "confidence": 0.91
            }
        ]
    }

    result = CodeReviewResult.model_validate(
        review_data
    )

    print()
    print("=" * 60)
    print("CODE REVIEW MODEL TEST")
    print("=" * 60)

    print()

    print(result)

    print()

    print("JSON:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()