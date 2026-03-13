import { useState } from "react";
import { login } from "../src/auth/authService";

export default function LoginForm({ onSuccess }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {

    e.preventDefault();

    setLoading(true);
    setError("");

    try {

      const token = await login(email, password);

      localStorage.setItem("access_token", token.access_token);

      onSuccess(token);

    } catch (err) {

      setError(err.message);

    }

    setLoading(false);

  };

  return (

    <form
      onSubmit={handleSubmit}
      className="bg-white p-8 rounded shadow w-96"
    >

      <h2 className="text-xl font-bold mb-6">
        LegalMind Login
      </h2>

      {error && (
        <div className="text-red-500 mb-4">
          {error}
        </div>
      )}

      <input
        type="email"
        placeholder="Email"
        className="border p-2 w-full mb-4 rounded"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        className="border p-2 w-full mb-4 rounded"
        value={password}
        onChange={(e)=>setPassword(e.target.value)}
      />

      <button
        type="submit"
        disabled={loading}
        className="bg-indigo-600 text-white w-full py-2 rounded"
      >
        {loading ? "Signing in..." : "Login"}
      </button>

    </form>

  );

}