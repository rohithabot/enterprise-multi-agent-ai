import { useState } from "react";
import { Bot, Send, User, Building2 } from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8002/chat";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! Ask me about HR policies or employee information.",
      agent: "system",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event.preventDefault();

    const text = question.trim();

    if (!text || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          agent: data.agent,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to connect to the AI backend.",
          agent: "error",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <Building2 size={28} />
          <div>
            <h2>Enterprise AI</h2>
            <p>Multi-Agent Assistant</p>
          </div>
        </div>

        <h4>AVAILABLE AGENTS</h4>

        <div className="agent-item">
          <Bot size={20} />
          HR Policy Agent
        </div>

        <div className="agent-item">
          <User size={20} />
          Employee Data Agent
        </div>

        <div className="sidebar-footer">
          Powered by LangGraph + Ollama
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1>Enterprise AI Assistant</h1>
            <p>Intelligent employee support powered by local AI</p>
          </div>

          <span className="status">● Local AI</span>
        </header>

        <section className="chat-container">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="avatar">
                {message.role === "user" ? (
                  <User size={20} />
                ) : (
                  <Bot size={20} />
                )}
              </div>

              <div className="message-content">
                {message.role === "assistant" &&
                  ["hr", "employee"].includes(message.agent) && (
                    <span className="agent-badge">
                      {message.agent === "hr"
                        ? "HR Policy Agent"
                        : "Employee Data Agent"}
                    </span>
                  )}

                <p>{message.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="avatar">
                <Bot size={20} />
              </div>

              <div className="message-content">
                Agent is thinking...
              </div>
            </div>
          )}
        </section>

        <form className="input-area" onSubmit={sendMessage}>
          <div className="input-wrapper">
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about HR policies or employee details..."
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>

          <p className="input-hint">
            AI responses are generated locally using Ollama.
          </p>
        </form>
      </main>
    </div>
  );
}

export default App;