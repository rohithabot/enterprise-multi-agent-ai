# Enterprise Multi-Agent AI Assistant

A full-stack multi-agent AI application built with LangGraph,
LangChain, Ollama, ChromaDB, FastAPI, and React.

## Features

- LangGraph supervisor for agent routing
- HR Policy Agent using Retrieval-Augmented Generation (RAG)
- Employee Data Agent using fictional JSON records
- Local Llama 3.2 model through Ollama
- ChromaDB vector search
- FastAPI REST API
- React chat interface
- Automated evaluation

## Architecture

React → FastAPI → LangGraph Supervisor
                       |
              +--------+--------+
              |                 |
         HR Policy Agent   Employee Agent
              |                 |
          ChromaDB          JSON Records
              |                 |
              +--------+--------+
                       |
                  Ollama LLM

The supervisor currently uses keyword-based routing.

## Tech Stack

Python, FastAPI, LangGraph, LangChain, Ollama,
ChromaDB, React, Vite, JavaScript.

## Setup

### Prerequisites

- Python 3.12
- Node.js
- Ollama

### Download models

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8002
```

### Frontend

From the project root, open another terminal:

```powershell
cd frontend\react-app
npm install
npm run dev
```

Open the address shown by Vite, normally localhost:5173.

## Evaluation

From the project root, with FastAPI running:

```powershell
.\backend\.venv\Scripts\python.exe evaluation\test_agents.py
```

### Results

- Total tests: 3
- Passed: 3
- Failed: 0
- Pass rate: 100%

The tests verify agent routing and expected answer keywords.
They do not constitute comprehensive hallucination evaluation.

## Example Questions

1. How many annual leave days do employees receive?
2. Which department does Rahul Sharma work in?
3. What is the company's annual leave policy?

## Future Enhancements

- LLM-based supervisor
- Conversation memory
- Authentication and authorization
- Streaming responses
- Expanded evaluation suite
- Docker deployment

## Note

This project uses fictional employee data and sample HR policies.