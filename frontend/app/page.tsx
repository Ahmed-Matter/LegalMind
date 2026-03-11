"use client";

import { useState } from "react";
import UploadPanel from "./components/UploadPanel";

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<{ role: string; text: string }[]>(
    [],
  );

  const sendMessage = async () => {
    if (!message) return;

    const userMessage = { role: "user", text: message };

    setMessages((prev) => [...prev, userMessage]);

    const response = await fetch(
      `http://localhost:8000/chat?question=${message}`,
      {
        method: "POST",
      },
    );

    const data = await response.json();

    const aiMessage = {
      role: "assistant",
      text: data.answer,
    };

    setMessages((prev) => [...prev, aiMessage]);

    setMessage("");
  };

  return (
    <div className="flex h-screen">
      <UploadPanel />

      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-6 overflow-y-auto bg-gray-100">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`mb-3 ${
                msg.role === "user" ? "text-right" : "text-left"
              }`}
            >
              <span className="inline-block bg-white p-3 rounded shadow">
                {msg.text}
              </span>
            </div>
          ))}
        </div>

        <div className="p-4 border-t flex gap-2">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-1 border p-2 rounded"
            placeholder="Ask a legal question..."
          />

          <button
            onClick={sendMessage}
            className="bg-blue-500 text-white px-4 rounded"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
