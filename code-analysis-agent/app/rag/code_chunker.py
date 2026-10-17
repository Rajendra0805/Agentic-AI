from dataclasses import dataclass


@dataclass
class CodeChunk:
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    content: str


class CodeChunker:

    def __init__(
        self,
        chunk_size: int = 100,
        overlap: int = 20
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(
        self,
        file_path: str,
        content: str
    ) -> list[CodeChunk]:

        lines = content.splitlines()

        chunks = []

        start = 0
        chunk_number = 0

        while start < len(lines):

            end = min(
                start + self.chunk_size,
                len(lines)
            )

            chunk_lines = lines[start:end]

            chunk = CodeChunk(
                chunk_id=f"{file_path}:{chunk_number}",
                file_path=file_path,
                start_line=start + 1,
                end_line=end,
                content="\n".join(chunk_lines)
            )

            chunks.append(chunk)

            chunk_number += 1

            if end == len(lines):
                break

            start = end - self.overlap

        return chunks