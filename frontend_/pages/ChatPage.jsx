import { useState } from "react";
import UploadPanel from "../components/UploadPanel";

export default function ChatPage({ messages, loading, onSend, onLogout }) {

  const [message, setMessage] = useState("");

  const sendMessage = () => {

    if (!message.trim()) return;

    onSend(message);

    setMessage("");

  };

  return (

    <div className="flex h-screen">

      {/* Sidebar */}
      <UploadPanel />

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">

        {/* Header */}
        <div className="p-4 border-b flex justify-between bg-white">

          <h2 className="font-bold text-lg">
            LegalMind AI
          </h2>

          <button
            onClick={onLogout}
            className="bg-red-500 text-white px-3 py-1 rounded"
          >
            Logout
          </button>

        </div>

        {/* Messages */}
        <div className="flex-1 p-6 overflow-y-auto bg-gray-100">

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`mb-3 ${
                msg.role === "user"
                  ? "text-right"
                  : "text-left"
              }`}
            >

              <span className="inline-block bg-white p-3 rounded shadow">

                {msg.text}

              </span>

            </div>

          ))}

          {loading && (
            <p className="text-gray-500">AI thinking...</p>
          )}

        </div>

        {/* Input */}
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