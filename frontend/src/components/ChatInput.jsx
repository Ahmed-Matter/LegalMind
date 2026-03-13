import { useState } from "react";

export default function ChatInput({messages,setMessages,user}){

  const [question,setQuestion] = useState("");
  const [loading,setLoading] = useState(false);

  const askQuestion = async ()=>{

    if(!question.trim()) return;

    setLoading(true);

    const userMessage = {
      role:"user",
      text:question
    };

    setMessages(prev => [...prev,userMessage]);

    try{

      const res = await fetch(
        `http://localhost:8000/chat?question=${encodeURIComponent(question)}`,
        {
          method:"POST",
          headers:{
            Authorization:`Bearer ${localStorage.getItem("access_token")}`
          }
        }
      );

      const data = await res.json();

      const aiMessage = {
        role:"ai",
        text:data.answer
      };

      setMessages(prev => [...prev,aiMessage]);

    }
    catch{

      setMessages(prev=>[
        ...prev,
        {role:"ai",text:"Error contacting AI service"}
      ]);

    }

    setQuestion("");
    setLoading(false);

  };

  return(

    <div className="flex flex-1 gap-2">

      <input
        value={question}
        onChange={(e)=>setQuestion(e.target.value)}
        placeholder="Ask a legal question..."
        className="flex-1 border p-2 rounded"
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
