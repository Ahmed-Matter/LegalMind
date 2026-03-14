import { useState } from "react";

export default function ChatInput({ messages, setMessages }) {

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = () => {

    if (!question.trim()) return;

    setLoading(true);

    const userMessage = {
      role: "user",
      text: question
    };

    const aiMessage = {
      role: "ai",
      text: ""
    };

    // add both messages in ONE state update
    setMessages(prev => [...prev, userMessage, aiMessage]);

    const sessionId = "user-session-1";

    const eventSource = new EventSource(
      `http://localhost:8000/chat-stream?question=${encodeURIComponent(question)}&session_id=${sessionId}`
    );

    eventSource.onmessage = (event) => {

      if (event.data === "[DONE]") {
        eventSource.close();
        setLoading(false);
        return;
      }

      setMessages(prev => {

        const updated = [...prev];

        // append text only to last AI message
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          text: updated[updated.length - 1].text + event.data
        };

        return updated;

      });

    };

    eventSource.onerror = () => {
      eventSource.close();
      setLoading(false);
    };

    setQuestion("");

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