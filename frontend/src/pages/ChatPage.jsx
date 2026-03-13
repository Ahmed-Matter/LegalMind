import { useState } from "react";
import MessageList from "../components/MessageList";
import ChatInput from "../components/ChatInput";
import UploadButton from "../components/UploadButton";

export default function ChatPage({ user, logout }) {

  const [messages,setMessages] = useState([]);
  const [files,setFiles] = useState([]);

  return(

    <div className="flex h-screen bg-gray-100">

      {/* Sidebar */}

      <div className="w-64 bg-white border-r p-4">

        <h3 className="font-bold mb-3">Documents</h3>

        {files.length === 0 && (
          <p className="text-gray-500">No files uploaded</p>
        )}

        {files.map((f,index)=>(
          <div key={index} className="p-2 border rounded mb-2">
            {f.filename}
          </div>
        ))}

      </div>


      {/* Chat Area */}

      <div className="flex-1 flex flex-col">

        <MessageList messages={messages}/>

        <div className="border-t p-4 flex gap-2 items-center">

          <UploadButton setFiles={setFiles}/>

          <ChatInput
            messages={messages}
            setMessages={setMessages}
            user={user}
          />

          <button
            onClick={logout}
            className="bg-red-500 text-white px-3 py-2 rounded"
          >
            Logout
          </button>

        </div>

      </div>

    </div>

  );

}
