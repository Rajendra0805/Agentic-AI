
from pprint import pprint

from app.documentation.documentation_toolkit import (
    DocumentationToolkit,
)

REPOSITORY_PATH = "sample-repository"

toolkit = DocumentationToolkit(REPOSITORY_PATH)
results = toolkit.inspect_repository()

print("Repository inspection summary:")
print(f"Tools attempted: {results['tools_attempted']}")
print(f"Tools succeeded: {results['tools_succeeded']}")
print(f"Tools failed: {results['tools_failed']}")

pprint(results["inspection_results"])
