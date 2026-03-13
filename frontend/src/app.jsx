import { useState,useEffect } from "react";

import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";

function App(){

  const [user,setUser] = useState(null);

  useEffect(()=>{

    const token = localStorage.getItem("access_token");

    if(token)
      setUser({token});

  },[]);

  if(!user)
    return <LoginPage onLogin={setUser}/>;

  return <ChatPage user={user} logout={()=>{

    localStorage.removeItem("access_token");
    setUser(null);

  }}/>;

}

export default App;
