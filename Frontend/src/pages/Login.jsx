import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const API_URL = "http://127.0.0.1:8000/api/";
  const login = async (username, password) => {
    const response = await axios.post(`${API_URL}auth/token/`, { username, password });
    return response.data.access;
  };
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const { login: authenticate } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setCredentials({ ...credentials, [e.target.name]: e.target.value });

  const handleLogin = async () => {
    try {
      const token = await login(credentials.username, credentials.password);
      authenticate(token);
      navigate("/dashboard");  // ✅ Navigate after successful login
    } catch (err) {
      setError("Invalid credentials. Try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0f172a] via-[#1e293b] to-[#334155] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-7">
        <p className="text-xs uppercase tracking-wider text-slate-500">AigesX Platform</p>
        <h2 className="text-2xl font-bold mt-1 text-slate-800">Fuzzing-as-a-Service Login</h2>
        <p className="text-sm text-slate-500 mt-1 mb-5">Access target intake, execution queue, and vulnerability findings.</p>
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <input type="text" name="username" placeholder="Username" onChange={handleChange} className="w-full border border-slate-200 rounded p-2 mb-2" />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} className="w-full border border-slate-200 rounded p-2 mb-3" />
        <button onClick={handleLogin} className="w-full bg-slate-900 text-white p-2 rounded hover:bg-slate-800">Login</button>
      </div>
    </div>
  );
};

export default Login;
