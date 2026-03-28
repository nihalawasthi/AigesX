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
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-bold mb-4">Login</h2>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <input type="text" name="username" placeholder="Username" onChange={handleChange} className="w-full border rounded p-2 mb-2" />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} className="w-full border rounded p-2 mb-2" />
        <button onClick={handleLogin} className="w-full bg-blue-500 text-white p-2 rounded">Login</button>
      </div>
    </div>
  );
};

export default Login;
