import { useEffect, useRef } from "react";

export default function MessageList({ messages }) {

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (

    <div className="flex-1 p-6 overflow-y-auto">

      {messages.map((msg, index) => (

        <div
          key={index}
          className={`mb-3 ${
            msg.role === "user" ? "text-right" : "text-left"
          }`}
        >

          <span className="inline-block bg-white p-3 rounded shadow">

            {msg.text || "AI typing..."}

          </span>

        </div>

      ))}

      <div ref={bottomRef} />

    </div>

  );

}
