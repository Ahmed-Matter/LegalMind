import { useState } from "react";
import { handleAuthError } from "../services/authService";

export default function ChatInput({ messages, setMessages }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem("access_token");

  // const askQuestion = () => {
  //   if (!question.trim()) return;

  //   setLoading(true);

  //   const userMessage = {
  //     role: "user",
  //     text: question,
  //   };

  //   const aiMessage = {
  //     role: "ai",
  //     text: "",
  //   };

  //   const token = localStorage.getItem("access_token");
  //   setMessages((prev) => [...prev, userMessage, aiMessage]);

  //   const sessionId = "user-session-1";

  //   const eventSource = new EventSource(
  //     `http://localhost:8000/chat-stream?question=${encodeURIComponent(question)}&session_id=${sessionId}&token=${token}`,
  //   );

  //   eventSource.onmessage = (event) => {
  //     if (event.data === "[DONE]") {
  //       eventSource.close();
  //       setLoading(false);

  //       //  attach sources
  //       setMessages((prev) => {
  //         const updated = [...prev];

  //         updated[updated.length - 1] = {
  //           ...updated[updated.length - 1],
  //           sources: lastSourcesRef.current || [],
  //         };

  //         return updated;
  //       });

  //       return;
  //     }

  //     setMessages((prev) => {
  //       const updated = [...prev];

  //       // append text only to last AI message
  //       updated[updated.length - 1] = {
  //         ...updated[updated.length - 1],
  //         text: updated[updated.length - 1].text + event.data,
  //       };

  //       return updated;
  //     });
  //   };

  //   eventSource.onerror = (err) => {
  //     console.log("SSE error:", err);

  //     eventSource.close();
  //     setLoading(false);
  //   };

  //   setQuestion("");
  // };
  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);

    const token = localStorage.getItem("access_token");
    if (!token) {
      handleAuthError();
      return;
    }
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
