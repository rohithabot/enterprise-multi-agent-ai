from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.multi_agent import ask_multi_agent


app = FastAPI(
    title="Enterprise Multi-Agent AI",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Enterprise Multi-Agent AI API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    result = ask_multi_agent(request.question)

    return {
        "question": request.question,
        "agent": result["agent"],
        "answer": result["answer"]
    }