import os
from dataclasses import dataclass
from typing import List, Tuple

import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Optional LLM providers
LLM_PROVIDER = None
OPENAI_READY = False
GROQ_READY = False

try:
    from langchain_openai import ChatOpenAI
    OPENAI_READY = True
except Exception:
    pass

try:
    from langchain_groq import ChatGroq
    GROQ_READY = True
except Exception:
    pass


# ---------------------------
# Load Data (salary.txt, insurance.txt)
# ---------------------------
def load_data() -> Tuple[str, str]:
    with open("salary.txt", encoding="utf-8") as f:
        salary_text = f.read()
    with open("insurance.txt", encoding="utf-8") as f:
        insurance_text = f.read()
    return salary_text, insurance_text


def build_vectorstores(salary_text: str, insurance_text: str) -> Tuple[FAISS, FAISS]:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    salary_docs = [Document(page_content=salary_text.strip(), metadata={"topic": "salary", "source": "salary.txt"})]
    insurance_docs = [Document(page_content=insurance_text.strip(), metadata={"topic": "insurance", "source": "insurance.txt"})]
    salary_store = FAISS.from_documents(salary_docs, embeddings)
    insurance_store = FAISS.from_documents(insurance_docs, embeddings)
    return salary_store, insurance_store


# ---------------------------
# Agent Response Wrapper
# ---------------------------
@dataclass
class AgentResponse:
    answer: str
    sources: List[str]
    retrieved_snippets: List[str]


def get_llm():
    if os.getenv("OPENAI_API_KEY") and OPENAI_READY:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    if os.getenv("GROQ_API_KEY") and GROQ_READY:
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
    return None


def rag_answer(query: str, store: FAISS, system_instruction: str) -> AgentResponse:
    docs = store.similarity_search(query, k=3)
    retrieved_snippets = [d.page_content for d in docs]
    sources = list({d.metadata.get("source", "unknown") for d in docs})

    llm = get_llm()
    if llm is None:
        context = "\n".join(retrieved_snippets)
        template = (
            f"[Fallback Answer]\n"
            f"Based on the retrieved notes:\n\n"
            f"{context}\n\n"
            f"Summary: I used the retrieved text above to answer your query."
        )
        return AgentResponse(answer=template, sources=sources, retrieved_snippets=retrieved_snippets)

    messages = [
        ("system", system_instruction.strip()),
        ("user", f"Question: {query}\n\nUse ONLY this context:\n{chr(10).join(retrieved_snippets)}")
    ]
    result = llm.invoke(messages)
    return AgentResponse(answer=result.content, sources=sources, retrieved_snippets=retrieved_snippets)


def salary_agent(query: str, store: FAISS) -> AgentResponse:
    instruction = """
You are the Salary Agent. Answer ONLY salary-related questions using the salary context.
If not about salary, say you don’t have that information.
"""
    return rag_answer(query, store, instruction)


def insurance_agent(query: str, store: FAISS) -> AgentResponse:
    instruction = """
You are the Insurance Agent. Answer ONLY insurance-related questions using the insurance context.
If not about insurance, say you don’t have that information.
"""
    return rag_answer(query, store, instruction)


# ---------------------------
# Coordinator
# ---------------------------
SALARY_KEYWORDS = ["salary", "monthly", "annual", "deduction", "bonus", "net pay", "gross", "pf"]
INSURANCE_KEYWORDS = ["insurance", "coverage", "premium", "claim", "policy", "hospital", "cashless"]


def route_query(user_query: str) -> str:
    q = user_query.lower()
    if any(k in q for k in INSURANCE_KEYWORDS):
        return "insurance"
    if any(k in q for k in SALARY_KEYWORDS):
        return "salary"
    return "unknown"


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Multi-Agent RAG • Salary & Insurance", page_icon="🤖", layout="centered")
st.title("🤖 Multi-Agent RAG: Salary & Insurance")

@st.cache_resource(show_spinner=False)
def _init():
    salary_text, insurance_text = load_data()
    return build_vectorstores(salary_text, insurance_text)

salary_store, insurance_store = _init()

if "chat" not in st.session_state:
    st.session_state.chat = []

# Sidebar
with st.sidebar:
    st.subheader("LLM Status")
    if os.getenv("OPENAI_API_KEY") and OPENAI_READY:
        st.success("Using OpenAI (gpt-4o-mini)")
    elif os.getenv("GROQ_API_KEY") and GROQ_READY:
        st.success("Using Groq (llama-3.1-8b-instant)")
    else:
        st.warning("No API key found – fallback mode")

    st.markdown("---")
    st.markdown("**Sample Queries:**")
    if st.button("What is included in my insurance policy?"):
        st.session_state.chat.append(("user", "What is included in my insurance policy?"))
    if st.button("How do I calculate annual salary?"):
        st.session_state.chat.append(("user", "How do I calculate annual salary?"))

# Display chat
for role, text in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(text)

# Chat input
user_input = st.chat_input("Ask about salary or insurance...")
if user_input:
    st.session_state.chat.append(("user", user_input))

# If last is user → process
if st.session_state.chat and st.session_state.chat[-1][0] == "user":
    query = st.session_state.chat[-1][1]
    route = route_query(query)

    if route == "salary":
        result = salary_agent(query, salary_store)
    elif route == "insurance":
        result = insurance_agent(query, insurance_store)
    else:
        result = AgentResponse(
            answer="I can only handle questions about salary or insurance.",
            sources=[],
            retrieved_snippets=[]
        )

    st.session_state.chat.append(("assistant", result.answer))

    with st.chat_message("assistant"):
        st.markdown(result.answer)
        with st.expander("🔎 Retrieval details"):
            st.write(f"**Agent:** {route}")
            if result.sources:
                st.write("**Sources:**", ", ".join(result.sources))
            for snip in result.retrieved_snippets:
                st.code(snip.strip())

st.markdown("---")