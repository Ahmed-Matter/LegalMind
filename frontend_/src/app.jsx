import { useState } from "react";
import axios from "axios";

import LoginPage from "../pages/LoginPage";
import ChatPage from "../pages/ChatPage";

function App() {

  // authentication state
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem("access_token");
    return token ? { token } : null;
  });

  // chat state
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  /*
  LOGIN HANDLER
  called after successful login
  */
  const handleLogin = (tokenData) => {

    localStorage.setItem("access_token", tokenData.access_token);

    setUser({
      token: tokenData.access_token
    });

  };

  /*
  LOGOUT HANDLER
  */
  const handleLogout = () => {

    localStorage.removeItem("access_token");

    setUser(null);

    setMessages([]);

  };

  /*
  SEND MESSAGE TO BACKEND
  */
  const askQuestion = async (question) => {

    if (!question.trim()) return;

    const userMessage = {
      role: "user",
      text: question
    };

    setMessages(prev => [...prev, userMessage]);

    setLoading(true);

    try {

      const response = await axios.post(
        "http://localhost:8000/chat",
        null,
        {
          params: { question },
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
          }
        }
      );

      const aiMessage = {
        role: "ai",
        text: response.data.answer
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {

      setMessages(prev => [
        ...prev,
        {
          role: "ai",
          text: "Error contacting AI service."
        }
      ]);

    }

    setLoading(false);

  };

  /*
  ROUTING LOGIC
  */

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <ChatPage
      messages={messages}
      loading={loading}
      onSend={askQuestion}
      onLogout={handleLogout}
    />
  );

}

export default App;