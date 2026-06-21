from __future__ import annotations

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings


def build_embeddings(settings: Settings) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store(settings: Settings, collection_name: str | None = None) -> Chroma:
    return Chroma(
        collection_name=collection_name or settings.collection_name,
        persist_directory=settings.chroma_db_dir,
        embedding_function=build_embeddings(settings),
    )


def split_documents(settings: Settings, documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def index_documents(
    settings: Settings,
    documents: list[Document],
    collection_name: str | None = None,
) -> tuple[Chroma, int]:
    chunks = split_documents(settings, documents)
    vector_store = build_vector_store(settings, collection_name=collection_name)
    if chunks:
        vector_store.add_documents(chunks)
    return vector_store, len(chunks)


def clear_collection(settings: Settings, collection_name: str | None = None) -> None:
    vector_store = build_vector_store(settings, collection_name=collection_name)
    try:
        vector_store.delete_collection()
    except ValueError:
        return
