from __future__ import annotations

import io
from pathlib import Path

from langchain_core.documents import Document
from PyPDF2 import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_uploaded_file(file_name: str, file_bytes: bytes) -> list[Document]:
    extension = Path(file_name).suffix.lower()
    if extension == ".pdf":
        return _load_pdf(file_name, file_bytes)
    if extension in {".txt", ".md"}:
        return _load_text(file_name, file_bytes)
    raise ValueError(f"Unsupported file type: {extension}")


def _load_pdf(file_name: str, file_bytes: bytes) -> list[Document]:
    reader = PdfReader(io.BytesIO(file_bytes))
    documents: list[Document] = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_name,
                    "page": page_index,
                    "file_type": "pdf",
                },
            )
        )

    return documents


def _load_text(file_name: str, file_bytes: bytes) -> list[Document]:
    text = file_bytes.decode("utf-8", errors="ignore").strip()
    if not text:
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": file_name,
                "page": None,
                "file_type": Path(file_name).suffix.lower().lstrip("."),
            },
        )
    ]
