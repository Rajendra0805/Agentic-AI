DEFAULT_REVIEW_CATEGORIES = [
    "Security",
    "Architecture",
    "Performance",
    "Maintainability",
    "Reliability",
    "Code Quality"
]


REVIEW_CATEGORY_DESCRIPTIONS = {

    "Security": [
        "authentication",
        "authorization",
        "hard-coded secrets",
        "SQL injection",
        "unsafe input handling",
        "sensitive information exposure",
        "insecure configuration"
    ],

    "Architecture": [
        "layer violations",
        "business logic in controllers",
        "tight coupling",
        "incorrect dependency direction",
        "separation of concerns"
    ],

    "Performance": [
        "N+1 queries",
        "unnecessary database calls",
        "inefficient loops",
        "large allocations",
        "blocking operations"
    ],

    "Maintainability": [
        "duplicated logic",
        "large methods",
        "complex methods",
        "poor separation of responsibilities",
        "tight coupling"
    ],

    "Reliability": [
        "missing error handling",
        "null handling",
        "resource leaks",
        "unexpected exceptions",
        "failure handling"
    ],

    "Code Quality": [
        "poor naming",
        "magic values",
        "dead code",
        "complex conditions",
        "duplicated code"
    ]
}