from pathlib import Path
from typing import Any


class RepositoryTools:
    """
    Read-only tools for analyzing a source-code repository.
    """

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.exists():
            raise ValueError(
                f"Repository does not exist: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repository_path}"
            )

    def list_files(self) -> list[str]:
        """
        Return source/configuration files in the repository.
        """

        ignored_directories = {
            ".git",
            ".vs",
            "bin",
            "obj",
            "node_modules",
            ".venv",
            "__pycache__"
        }

        allowed_extensions = {
            ".cs",
            ".csproj",
            ".sln",
            ".json",
            ".xml",
            ".config",
            ".yml",
            ".yaml",
            ".md"
        }

        files = []

        for path in self.repository_path.rglob("*"):

            if not path.is_file():
                continue

            if any(
                ignored in path.parts
                for ignored in ignored_directories
            ):
                continue

            if path.suffix.lower() in allowed_extensions:
                files.append(
                    str(path.relative_to(self.repository_path))
                )

        return sorted(files)

    def find_project_files(self) -> list[str]:
        """
        Find .NET solution and project files.
        """

        results = []

        for path in self.repository_path.rglob("*"):

            if not path.is_file():
                continue

            if any(
                ignored in path.parts
                for ignored in {".git", "bin", "obj"}
            ):
                continue

            if path.suffix.lower() in {".sln", ".csproj"}:
                results.append(
                    str(path.relative_to(self.repository_path))
                )

        return sorted(results)

    def find_api_endpoints(self) -> list[dict[str, Any]]:
        """
        Detect common ASP.NET Core controller/API attributes.
        """

        results = []

        for path in self.repository_path.rglob("*.cs"):

            if any(
                ignored in path.parts
                for ignored in {".git", "bin", "obj"}
            ):
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except Exception:
                continue

            attributes = []

            for attribute in [
                "ApiController",
                "Route",
                "HttpGet",
                "HttpPost",
                "HttpPut",
                "HttpDelete",
                "HttpPatch"
            ]:
                if attribute in content:
                    attributes.append(attribute)

            if attributes:
                results.append({
                    "file": str(
                        path.relative_to(self.repository_path)
                    ),
                    "attributes": attributes
                })

        return results

    def find_database_usage(self) -> list[dict[str, Any]]:
        """
        Detect common database technologies/patterns.
        """

        patterns = [
            "DbContext",
            "AddDbContext",
            "EntityFrameworkCore",
            "SqlConnection",
            "Dapper",
            "UseSqlServer",
            "UseNpgsql",
            "UseMySql"
        ]

        results = []

        for path in self.repository_path.rglob("*.cs"):

            if any(
                ignored in path.parts
                for ignored in {".git", "bin", "obj"}
            ):
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except Exception:
                continue

            matches = [
                pattern
                for pattern in patterns
                if pattern in content
            ]

            if matches:
                results.append({
                    "file": str(
                        path.relative_to(self.repository_path)
                    ),
                    "patterns": matches
                })

        return results

    def find_dependencies(self) -> list[dict[str, Any]]:
        """
        Extract ProjectReference and PackageReference
        information from .csproj files.
        """

        results = []

        for path in self.repository_path.rglob("*.csproj"):

            if any(
                ignored in path.parts
                for ignored in {".git", "bin", "obj"}
            ):
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except Exception:
                continue

            project_references = []
            package_references = []

            lines = content.splitlines()

            for line in lines:

                line = line.strip()

                if "<ProjectReference" in line:
                    project_references.append(line)

                if "<PackageReference" in line:
                    package_references.append(line)

            results.append({
                "project": str(
                    path.relative_to(self.repository_path)
                ),
                "project_references": project_references,
                "package_references": package_references
            })

        return results

    def get_repository_summary(self) -> dict[str, Any]:
        """
        Run the initial deterministic repository analysis.
        """

        files = self.list_files()

        return {
            "repository": self.repository_path.name,
            "file_count": len(files),
            "files": files,
            "projects": self.find_project_files(),
            "api_endpoints": self.find_api_endpoints(),
            "database_usage": self.find_database_usage(),
            "dependencies": self.find_dependencies()
        }