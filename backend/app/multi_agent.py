import json
from pathlib import Path
from typing import Literal, TypedDict

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


# ============================================================
# 2. OLLAMA CONFIGURATION
# ============================================================

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


# ============================================================
# 3. LOAD HR POLICIES
# ============================================================

policy_text = (DATA_DIR / "hr_policies.txt").read_text(
    encoding="utf-8"
)

policy_documents = [
    Document(
        page_content=policy_text,
        metadata={"source": "hr_policies.txt"}
    )
]


# ============================================================
# 4. CREATE VECTOR DATABASE
# ============================================================

vector_store = Chroma.from_documents(
    documents=policy_documents,
    embedding=embeddings,
    collection_name="hr_policies"
)


# ============================================================
# 5. LOAD EMPLOYEE RECORDS
# ============================================================

employees = json.loads(
    (DATA_DIR / "employees.json").read_text(
        encoding="utf-8"
    )
)


# ============================================================
# 6. DEFINE LANGGRAPH STATE
# ============================================================

class AgentState(TypedDict):
    question: str
    route: str
    answer: str


# ============================================================
# 7. SUPERVISOR AGENT - FIXED ROUTING
# ============================================================

def supervisor(state: AgentState):
    question = state["question"].lower()

    hr_keywords = [
        "leave",
        "policy",
        "policies",
        "remote",
        "working hours",
        "benefits",
        "insurance",
        "holiday",
        "vacation",
        "sick",
        "approval",
        "work from home",
    ]

    employee_keywords = [
        "employee id",
        "department",
        "designation",
        "location",
        "rahul",
        "priya",
        "arjun",
        "manager",
        "employee details",
    ]

    # Check HR policy questions first
    if any(keyword in question for keyword in hr_keywords):
        return {"route": "hr"}

    # Check employee information questions
    if any(keyword in question for keyword in employee_keywords):
        return {"route": "employee"}

    # Default to HR agent
    return {"route": "hr"}


# ============================================================
# 8. HR POLICY AGENT - RAG
# ============================================================

def hr_agent(state: AgentState):
    question = state["question"]

    # Retrieve relevant HR policies
    docs = vector_store.similarity_search(
        question,
        k=1
    )

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    # Generate answer using retrieved context
    response = llm.invoke(
        f"""
You are an Enterprise HR Policy Assistant.

Your responsibility is to answer employee questions
using ONLY the company HR policy information provided.

Rules:
1. Use only the supplied policy context.
2. Do not invent company policies.
3. Give clear and concise answers.
4. If information is unavailable, say:
   "I could not find this information in the HR policies."
5. When answering questions about leave,
   provide the exact number of days mentioned.

HR POLICY CONTEXT:
{context}

EMPLOYEE QUESTION:
{question}

ANSWER:
"""
    )

    return {
        "answer": str(response.content)
    }


# ============================================================
# 9. EMPLOYEE DATA AGENT
# ============================================================

def employee_agent(state: AgentState):
    question = state["question"]

    response = llm.invoke(
        f"""
You are an Enterprise Employee Information Assistant.

Your responsibility is to answer questions using
ONLY the provided fictional employee records.

Rules:
1. Do not invent employee information.
2. Only use the employee records provided.
3. Answer clearly and concisely.
4. If employee information is unavailable,
   say "Employee information not found."

EMPLOYEE RECORDS:
{json.dumps(employees, indent=2)}

QUESTION:
{question}

ANSWER:
"""
    )

    return {
        "answer": str(response.content)
    }


# ============================================================
# 10. AGENT ROUTING
# ============================================================

def choose_agent(
    state: AgentState,
) -> Literal["hr_agent", "employee_agent"]:

    if state["route"] == "employee":
        return "employee_agent"

    return "hr_agent"


# ============================================================
# 11. BUILD LANGGRAPH WORKFLOW
# ============================================================

builder = StateGraph(AgentState)

# Register agents
builder.add_node("supervisor", supervisor)
builder.add_node("hr_agent", hr_agent)
builder.add_node("employee_agent", employee_agent)

# Start with supervisor
builder.add_edge(START, "supervisor")

# Route to the correct agent
builder.add_conditional_edges(
    "supervisor",
    choose_agent
)

# End workflow after agent response
builder.add_edge("hr_agent", END)
builder.add_edge("employee_agent", END)

# Compile workflow
multi_agent_graph = builder.compile()


# ============================================================
# 12. MAIN FUNCTION CALLED BY FASTAPI
# ============================================================

def ask_multi_agent(question: str):

    result = multi_agent_graph.invoke(
        {
            "question": question,
            "route": "",
            "answer": ""
        }
    )

    return {
        "agent": result["route"],
        "answer": result["answer"]
    }