import { useState } from "react";
import { handleAuthError } from "../services/authService";

export default function ChatInput({
  messages,
  setMessages,
  setCurrentQuestion,
  setLastAnswer,
}) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);

    const token = localStorage.getItem("access_token");

    const res = await fetch(
      "http://localhost:8000/chat?question=" + encodeURIComponent(question),
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (res.status === 401) {
      handleAuthError();
      return;
    }

    const data = await res.json();

    setCurrentQuestion(question);
    setLastAnswer(data.answer);

    setMessages((prev) => [
      ...prev,
      { role: "user", text: question },
      { role: "ai", text: data.answer, sources: data.sources },
    ]);

    setQuestion("");
    setLoading(false);
  };

  return (
    <div className="flex flex-1 gap-2">
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
        className="flex-1 border p-2 rounded"
        onKeyDown={(e) => {
          if (e.key === "Enter") askQuestion();
        }}
      />

      <button
        onClick={askQuestion}
        className="bg-indigo-600 text-white px-4 rounded"
      >
        Send
      </button>
    </div>
  );
}
