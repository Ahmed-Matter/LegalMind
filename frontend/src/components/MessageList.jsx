import { useEffect, useRef } from "react";

export default function MessageList({ messages, onSourceClick }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      {messages.map((msg, index) => (
        <div key={index} className="mb-3">
          <p>{msg.text}</p>

          {msg.sources && (
            <div className="mt-2">
              {msg.sources.map((s, i) => (
                <div
                  key={i}
                  className="text-blue-600 cursor-pointer text-sm hover:underline"
                  onClick={() => onSourceClick(s)} //  FIXED
                >
                  Source {i + 1}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      <div ref={bottomRef} />
    </div>
  );
}
