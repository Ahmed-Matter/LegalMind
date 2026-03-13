import { useState } from "react";
import { login } from "../services/authService";

export default function LoginForm({ onLogin }) {

  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");
  const [error,setError] = useState("");
  const [loading,setLoading] = useState(false);

  const handleSubmit = async (e)=>{

    e.preventDefault();

    setLoading(true);
    setError("");

    try{

      const data = await login(email,password);

      localStorage.setItem("access_token",data.access_token);

      onLogin(data);

    }catch(err){

      setError(err.message);

    }

    setLoading(false);
  };

  return(

    <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow w-96">

      <h2 className="text-2xl font-bold mb-4 text-center">
        LegalMind Login
      </h2>

      {error && <p className="text-red-500">{error}</p>}

      <input
        type="email"
        placeholder="Email"
        className="w-full p-2 border rounded mb-3"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        className="w-full p-2 border rounded mb-3"
        value={password}
        onChange={(e)=>setPassword(e.target.value)}
      />

      <button
        className="w-full bg-indigo-600 text-white p-2 rounded"
        disabled={loading}
      >
        {loading ? "Signing in..." : "Login"}
      </button>

    </form>

  );

}
