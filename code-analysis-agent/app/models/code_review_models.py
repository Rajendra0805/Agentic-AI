from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
    "Info"
]


Category = Literal[
    "Security",
    "Architecture",
    "Performance",
    "Maintainability",
    "Reliability",
    "Code Quality"
]


class ReviewFinding(BaseModel):

    category: Category

    severity: Severity

    title: str

    description: str

    file_path: str

    start_line: int | None = None

    end_line: int | None = None

    evidence: str

    recommendation: str

    confidence: float = Field(
        ge=0,
        le=1
    )


class CodeReviewResult(BaseModel):

    repository: str

    reviewed_scope: str

    summary: str

    findings: list[ReviewFinding] = Field(
        default_factory=list
    )