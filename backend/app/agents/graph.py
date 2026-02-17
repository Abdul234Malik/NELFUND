from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.rag.retriever import retrieve
from app.core.config import OPENAI_API_KEY  # noqa: F401


# -------- STATE --------
class AgentState(TypedDict):
    query: str
    intent: Optional[str]
    context: Optional[str]
    answer: Optional[str]
    sources: List[str]


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------- NODES --------
def classify_intent(state: AgentState):
    query = (state.get("query") or "").strip()
    if not query:
        return {"intent": "policy"}
    query_lower = query.lower()

    # If it looks like a question, always use the knowledge base
    if "?" in query:
        return {"intent": "policy"}
    if len(query.split()) > 2:
        return {"intent": "policy"}

    # Question-like words: if present, always treat as policy question
    question_indicators = [
        "what", "how", "when", "where", "who", "why", "which", "tell me", "explain",
        "eligibility", "application", "repayment", "loan", "nelfund", "require",
        "criteria", "process", "step", "document", "qualify", "apply", "info", "know",
    ]
    if any(ind in query_lower for ind in question_indicators):
        return {"intent": "policy"}

    # Only treat as greeting when query is exactly a greeting phrase (1–2 words)
    greetings = ["hello", "hi", "hey", "good morning", "good evening", "hey there", "hi there"]
    if query_lower in greetings:
        return {"intent": "greeting"}

    return {"intent": "policy"}


def retrieve_docs(state: AgentState):
    query = state["query"]
    print(f"[RETRIEVE] Query: {query}")
    
    docs = retrieve(query)
    print(f"[RETRIEVE] Retrieved {len(docs)} documents")

    if not docs:
        print("[RETRIEVE] WARNING: No documents retrieved! Database might be empty.")
        return {
            "context": "",
            "sources": []
        }

    context = "\n\n".join(
        [f"Source: {doc.metadata.get('source')}\n{doc.page_content}" for doc in docs]
    )

    sources = list(set(doc.metadata.get("source") for doc in docs))
    print(f"[RETRIEVE] Sources: {sources}")

    return {
        "context": context,
        "sources": sources
    }


def generate_answer(state: AgentState):
    if state["intent"] == "greeting":
        return {
            "answer": "Hello 👋 I can help you understand the NELFUND student loan. Ask me about eligibility, application steps, or repayment.",
            "sources": []
        }

    context = state.get("context", "")
    query = state["query"]
    
    print(f"[GENERATE] Query: {query}")
    print(f"[GENERATE] Context length: {len(context)} characters")
    print(f"[GENERATE] Sources: {state.get('sources', [])}")
    
    # If no context was retrieved, inform the user
    if not context or len(context.strip()) == 0:
        print("[GENERATE] WARNING: Empty context - no documents retrieved from database")
        return {
            "answer": "I apologize, but I couldn't find any relevant information in the knowledge base to answer your question. This might mean:\n\n1. The database needs to be populated with documents (run the ingestion script)\n2. Your question might need to be rephrased\n3. The information might not be available in the current documents\n\nPlease try asking about NELFUND student loan eligibility, application process, or repayment plans.",
            "sources": []
        }

    prompt = f"""
You are an assistant answering questions about the Nigerian Student Loan (NELFUND).

Rules:
- Answer ONLY from the context provided below
- If the answer is not in the documents, say "I don't have that specific information in the available documents, but based on what I know about NELFUND, I can tell you..."
- Be clear, concise, and helpful
- Cite sources when applicable
- If the context doesn't contain the answer, still try to provide helpful general guidance about NELFUND

Context:
{context}

Question:
{query}

Answer:
"""

    try:
        response = llm.invoke(prompt)
        answer = response.content
        print(f"[GENERATE] Generated answer (first 100 chars): {answer[:100]}...")
        return {
            "answer": answer
        }
    except Exception as e:
        print(f"[GENERATE] Error calling LLM: {e}")
        import traceback
        traceback.print_exc()
        return {
            "answer": f"Error generating answer: {str(e)}",
            "sources": state.get("sources", [])
        }


# -------- GRAPH --------
graph = StateGraph(AgentState)

graph.add_node("classify", classify_intent)
graph.add_node("retrieve", retrieve_docs)
graph.add_node("answer", generate_answer)

graph.set_entry_point("classify")

graph.add_conditional_edges(
    "classify",
    lambda state: state["intent"],
    {
        "greeting": "answer",
        "policy": "retrieve"
    }
)

graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

agent = graph.compile()
