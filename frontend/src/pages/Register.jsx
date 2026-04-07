import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    reg_id: "",
    name: "",
    department: "",
    district: "",
    father_name: "",
    mother_name: "",
    student_email: "",
    parent_email: "",
    parent_phone: "",
    warden_maylady_email: "",
    password: "",
  });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const { data } = await register(form);
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
      window.location.reload();
    } catch (e) {
      const d = e.response?.data?.detail;
      const msg = typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg || x.loc?.join(".")).join(". ") : e.message || "Registration failed";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Student Registration</h1>
        <p className="subtitle">Create your hostel leave account</p>
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Reg ID
            <input
              placeholder="e.g. 21BCS001"
              value={form.reg_id}
              onChange={(e) => setForm({ ...form, reg_id: e.target.value })}
              required
            />
          </label>
          <label>
            Full Name
            <input
              placeholder="e.g. Priya Selvam"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label>
            Department
            <input
              placeholder="e.g. B.Sc Computer Science"
              value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              required
            />
          </label>
          <label>
            District
            <input
              placeholder="e.g. Chennai"
              value={form.district}
              onChange={(e) => setForm({ ...form, district: e.target.value })}
              required
            />
          </label>
          <label>
            Father Name
            <input
              placeholder="e.g. R. Selvam"
              value={form.father_name}
              onChange={(e) => setForm({ ...form, father_name: e.target.value })}
              required
            />
          </label>
          <label>
            Mother Name
            <input
              placeholder="e.g. L. Devi"
              value={form.mother_name}
              onChange={(e) => setForm({ ...form, mother_name: e.target.value })}
              required
            />
          </label>
          <label>
            Student Email
            <input
              type="email"
              placeholder="student@college.edu"
              value={form.student_email}
              onChange={(e) => setForm({ ...form, student_email: e.target.value })}
              required
            />
          </label>
          <label>
            Parent Email
            <input
              type="email"
              placeholder="parent@gmail.com"
              value={form.parent_email}
              onChange={(e) => setForm({ ...form, parent_email: e.target.value })}
              required
            />
          </label>
          <label>
            Parent Phone (required - receives leave request via WhatsApp)
            <input
              type="tel"
              placeholder="e.g. 9876543210"
              value={form.parent_phone}
              onChange={(e) => setForm({ ...form, parent_phone: e.target.value })}
              required
            />
          </label>
          <label>
            Warden Maylady Email
            <input
              type="email"
              placeholder="warden.maylady@hostel.edu"
              value={form.warden_maylady_email}
              onChange={(e) => setForm({ ...form, warden_maylady_email: e.target.value })}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              placeholder="Min 6 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={6}
            />
          </label>
          {err && <p className="error">{err}</p>}
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? "Registering..." : "Create Account"}
          </button>
        </form>
        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
