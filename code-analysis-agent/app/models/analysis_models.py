from pydantic import BaseModel, Field


class Finding(BaseModel):
    category: str
    severity: str
    title: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    recommendation: str


class ProjectDependencies(BaseModel):
    project: str
    project_references: list[str] = Field(default_factory=list)
    package_references: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    repository: str

    architecture_pattern: str

    architecture_confidence: float = Field(
        ge=0,
        le=1
    )

    summary: str

    projects: list[str] = Field(
        default_factory=list
    )

    api_files: list[str] = Field(
        default_factory=list
    )

    database_files: list[str] = Field(
        default_factory=list
    )

    dependencies: list[ProjectDependencies] = Field(
        default_factory=list
    )

    findings: list[Finding] = Field(
        default_factory=list
    )