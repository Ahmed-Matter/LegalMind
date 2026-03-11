import { useState } from "react";
import axios from "axios";

function App() {
  const [loading,setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const askQuestion = async () => {
    setLoading(true);
    const userMessage = {
      role: "user",
      text: question
    };

    setMessages(prev => [...prev, userMessage]);

    const response = await axios.post(
      "http://localhost:8000/chat",
      null,
      { params: { question: question } }
    );

    const aiMessage = {
      role: "ai",
      text: response.data.answer
    };

    setMessages(prev => [...prev, aiMessage]);

    setQuestion("");
    setLoading(false);
  };

  return (

    <div style={{width:"600px", margin:"auto"}}>

      <h2>LegalMind AI</h2>
      {loading && <p>AI thinking...</p>}
      <div style={{border:"1px solid #ccc", padding:"10px", height:"400px", overflow:"auto"}}>

        {messages.map((m, index) => (

          <div key={index} style={{marginBottom:"10px"}}>

            <b>{m.role === "user" ? "You" : "AI"}:</b>

            <div>{m.text}</div>

          </div>

        ))}

      </div>

      <input
        value={question}
        onChange={(e)=>setQuestion(e.target.value)}
        style={{width:"80%"}}
      />

      <button onClick={askQuestion}>
        Ask
      </button>

    </div>
  );
}

export default App;