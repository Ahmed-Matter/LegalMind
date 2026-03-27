import { useState, useEffect } from "react";
import MessageList from "../components/MessageList";
import ChatInput from "../components/ChatInput";
import UploadButton from "../components/UploadButton";
import PdfViewer from "../components/PdfViewer";

function handleAuthError() {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
}

export default function ChatPage({ user, logout }) {
  const [messages, setMessages] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null);

  const [currentQuestion, setCurrentQuestion] = useState("");
  const [lastAnswer, setLastAnswer] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      handleAuthError();
      return;
    }

    fetch("http://localhost:8000/documents", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.status === 401) {
          handleAuthError();
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setFiles(data);
      })
      .catch(console.error);
  }, []);

  const handleSourceClick = (source) => {
    const doc = files.find((f) => f.id === source.document_id);
    if (!doc) return;

    const lastUserMessage = [...messages]
      .reverse()
      .find((m) => m.role === "user");

    const lastAiMessage = [...messages].reverse().find((m) => m.role === "ai");

    setSelectedSource({
      url: `http://localhost:8000/files/${doc.filename}`,
      page: source.page,
      text: source.text,
      question: lastUserMessage?.text || "",
      answer: lastAiMessage?.text || "",
    });
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* LEFT: documents */}
      <div className="w-64 bg-white border-r p-4">
        <h3 className="font-bold mb-3">Documents</h3>

        {files.length === 0 && (
          <p className="text-gray-500">No files uploaded</p>
        )}

        {files.map((f) => (
          <div key={f.id} className="p-2 border rounded mb-2">
            {f.filename}
          </div>
        ))}
      </div>

      {/* CENTER: chat */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} onSourceClick={handleSourceClick} />

        <div className="border-t p-4 flex gap-2 items-center">
          <UploadButton setFiles={setFiles} />

          <ChatInput
            messages={messages}
            setMessages={setMessages}
            setCurrentQuestion={setCurrentQuestion}
            setLastAnswer={setLastAnswer}
          />

          <button
            onClick={logout}
            className="bg-red-500 text-white px-3 py-2 rounded"
          >
            Logout
          </button>
        </div>
      </div>

      {/* RIGHT: PDF Viewer */}
      {selectedSource && (
        <div className="w-1/2 border-l">
          <PdfViewer
            fileUrl={selectedSource.url}
            page={selectedSource.page}
            highlightText={selectedSource.text}
            question={selectedSource.question}
            answer={selectedSource.answer}
          />
        </div>
      )}
    </div>
  );
}
