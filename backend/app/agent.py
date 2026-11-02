from langchain.agents import create_agent
from langchain_ollama import ChatOllama

# Local language model
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

# LangChain agent using LangGraph internally
agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=(
        "You are a helpful enterprise AI assistant. "
        "Answer questions clearly and concisely. "
        "Do not invent company policies or employee information."
    )
)


def ask_agent(question: str) -> str:
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    return response["messages"][-1].content