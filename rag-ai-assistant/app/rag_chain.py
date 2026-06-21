from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser


SYSTEM_PROMPT = """You are a helpful RAG-based AI assistant.
Answer only from the provided context. If the answer is not in the context,
say that you do not know based on the uploaded documents.
Be concise, accurate, and cite source names or page numbers when useful."""


PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Question:\n{question}\n\nRetrieved context:\n{context}\n\nAnswer:",
        ),
    ]
)


def format_documents(documents: list[Document]) -> str:
    formatted: list[str] = []
    for index, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown source")
        page = doc.metadata.get("page")
        page_label = f", page {page}" if page else ""
        formatted.append(
            f"[{index}] Source: {source}{page_label}\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


def build_answer_chain(llm: BaseChatModel) -> Runnable:
    return PROMPT | llm | StrOutputParser()


def answer_question(question: str, retriever: Runnable, llm: BaseChatModel) -> dict:
    retrieved_docs = retriever.invoke(question)
    context = format_documents(retrieved_docs)
    chain = build_answer_chain(llm)
    answer = chain.invoke({"question": question, "context": context})
    return {"answer": answer, "sources": retrieved_docs}
