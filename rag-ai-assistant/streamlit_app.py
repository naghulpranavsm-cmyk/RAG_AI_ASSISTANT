from __future__ import annotations

import streamlit as st

from app.config import get_settings
from app.document_loader import SUPPORTED_EXTENSIONS, load_uploaded_file
from app.llm import build_llm
from app.rag_chain import answer_question
from app.vector_store import build_vector_store, clear_collection, index_documents


st.set_page_config(page_title="RAG AI Assistant", page_icon="AI", layout="wide")


def initialize_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("indexed_chunks", 0)
    st.session_state.setdefault("collection_name", get_settings().collection_name)


def render_sidebar() -> None:
    settings = get_settings()

    with st.sidebar:
        st.title("Knowledge Base")
        st.caption("Upload PDFs, research papers, notes, or text documents.")

        collection_name = st.text_input(
            "Collection",
            value=st.session_state.collection_name,
            help="Use different collection names for different projects.",
        )
        st.session_state.collection_name = collection_name.strip() or settings.collection_name

        uploaded_files = st.file_uploader(
            "Documents",
            type=[extension.lstrip(".") for extension in SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            index_clicked = st.button("Index Documents", type="primary", use_container_width=True)
        with col2:
            clear_clicked = st.button("Clear Index", use_container_width=True)

        if clear_clicked:
            clear_collection(settings, st.session_state.collection_name)
            st.session_state.indexed_chunks = 0
            st.session_state.messages = []
            st.success("Vector index cleared.")

        if index_clicked:
            if not uploaded_files:
                st.warning("Upload at least one document first.")
                return

            documents = []
            skipped_files = []
            with st.spinner("Reading and indexing documents..."):
                for uploaded_file in uploaded_files:
                    try:
                        documents.extend(
                            load_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
                        )
                    except Exception as exc:
                        skipped_files.append(f"{uploaded_file.name}: {exc}")

                if not documents:
                    st.error("No extractable text was found in the uploaded files.")
                    return

                _, chunk_count = index_documents(
                    settings,
                    documents,
                    collection_name=st.session_state.collection_name,
                )
                st.session_state.indexed_chunks += chunk_count

            st.success(f"Indexed {chunk_count} chunks from {len(documents)} document sections.")
            if skipped_files:
                st.warning("Some files were skipped: " + "; ".join(skipped_files))

        st.divider()
        st.subheader("Runtime")
        st.write(f"LLM provider: `{settings.llm_provider}`")
        st.write(f"Embedding model: `{settings.embedding_model}`")
        st.write(f"Indexed chunks this session: `{st.session_state.indexed_chunks}`")


def render_chat() -> None:
    settings = get_settings()

    st.title("RAG AI Assistant")
    st.caption("Ask questions grounded in your uploaded PDFs, papers, documents, and notes.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input("Ask a question about your documents")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching documents and generating an answer..."):
                vector_store = build_vector_store(
                    settings,
                    collection_name=st.session_state.collection_name,
                )
                retriever = vector_store.as_retriever(
                    search_kwargs={"k": settings.retrieval_k}
                )
                llm = build_llm(settings)
                result = answer_question(question, retriever, llm)

            st.markdown(result["answer"])
            render_sources(result["sources"])
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                }
            )
        except Exception as exc:
            message = f"Could not answer yet: {exc}"
            st.error(message)
            st.session_state.messages.append({"role": "assistant", "content": message})


def render_sources(sources) -> None:
    if not sources:
        return

    with st.expander("Sources", expanded=False):
        for index, doc in enumerate(sources, start=1):
            source = doc.metadata.get("source", "unknown source")
            page = doc.metadata.get("page")
            page_label = f", page {page}" if page else ""
            st.markdown(f"**{index}. {source}{page_label}**")
            preview = doc.page_content[:700].strip()
            if len(doc.page_content) > 700:
                preview += "..."
            st.write(preview)


def main() -> None:
    initialize_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
