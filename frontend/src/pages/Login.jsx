import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [form, setForm] = useState({ reg_id_or_email: "", password: "" });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const { data } = await login(form);
      localStorage.setItem("token", data.access_token);
      loginUser(data.user);
      if (data.user.role === "warden") {
        navigate("/warden");
      } else {
        navigate("/dashboard");
      }
    } catch (e) {
      const d = e.response?.data?.detail;
      const msg = typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg || x.loc?.join(".")).join(". ") : e.message || "Login failed";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Login</h1>
        <p className="subtitle">Sign in with your Reg ID or email</p>
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Reg ID or Email
            <input
              placeholder="e.g. 21BCS001 or student@college.edu"
              value={form.reg_id_or_email}
              onChange={(e) => setForm({ ...form, reg_id_or_email: e.target.value })}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              placeholder="Enter your password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </label>
          {err && <p className="error">{err}</p>}
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? "Logging in..." : "Sign In"}
          </button>
        </form>
        <p className="auth-link">
          New student? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
