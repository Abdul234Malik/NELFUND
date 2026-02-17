from app.core.config import OPENAI_API_KEY  # noqa: F401

from langchain_openai import ChatOpenAI
from app.rag.retriever import retrieve


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

SYSTEM_PROMPT = """
You are an assistant that answers questions about the Nigerian Student Loan (NELFUND).

Rules:
- Use ONLY the provided context
- If the answer is not in the documents, say you don't know
- Cite sources clearly
"""

def answer_question(query: str):
    docs = retrieve(query)

    context = "\n\n".join(
        [f"Source: {doc.metadata.get('source')}\n{doc.page_content}" for doc in docs]
    )

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{query}

Answer with citations:
"""

    response = llm.invoke(prompt)

    sources = list(set(doc.metadata.get("source") for doc in docs))

    return {
        "answer": response.content,
        "sources": sources
    }
