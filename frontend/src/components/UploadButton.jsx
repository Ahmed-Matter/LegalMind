import { useRef } from "react";
import { handleAuthError } from "../services/authService";

export default function UploadButton({setFiles}){

  const fileInput = useRef();

  const uploadFile = async (file)=>{

    const formData = new FormData();
    formData.append("file",file);

    const res = await fetch("http://localhost:8000/upload",{
      method:"POST",
      body:formData,
      headers:{
        Authorization:`Bearer ${localStorage.getItem("access_token")}`
      }
    });
    if(res.status===401){
      handleAuthError();
      return;
    }

    const data = await res.json();

    setFiles(prev => [...prev,data]);

  };

  return(

    <>
      <button
        onClick={()=>fileInput.current.click()}
        className="bg-gray-200 px-3 py-2 rounded"
      >
        +
      </button>

      <input
        type="file"
        ref={fileInput}
        hidden
        onChange={(e)=>uploadFile(e.target.files[0])}
      />
    </>

  );

}
