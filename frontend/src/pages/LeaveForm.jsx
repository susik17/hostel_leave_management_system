import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createLeave, testWhatsApp } from "../api";
import { useAuth } from "../context/AuthContext";

export default function LeaveForm() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [form, setForm] = useState({
    reason: "",
    departure_datetime: "",
    arrival_datetime: "",
    parent_phone: "",
  });
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [testWaLoading, setTestWaLoading] = useState(false);
  const [testWaMsg, setTestWaMsg] = useState("");

  useEffect(() => {
    const now = new Date();
    const dep = new Date(now.getTime() + 60 * 60 * 1000);
    const arr = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000);
    const toLocal = (d) => d.toISOString().slice(0, 16);
    setForm((f) => ({
      reason: f.reason || "Family function",
      departure_datetime: f.departure_datetime || toLocal(dep),
      arrival_datetime: f.arrival_datetime || toLocal(arr),
      parent_phone: f.parent_phone || user?.parent_phone || "",
    }));
  }, [user?.parent_phone]);

  const handleTestWhatsApp = async () => {
    const raw = (form.parent_phone || user?.parent_phone || "").trim();
    const phone = raw.replace(/\D/g, "").slice(-10);
    if (!phone) {
      setTestWaMsg("✗ Enter parent phone first.");
      return;
    }
    setTestWaMsg("");
    setTestWaLoading(true);
    try {
      const res = await testWhatsApp(phone);
      if (res.data?.ok) {
        setTestWaMsg(`✓ Test sent to ${phone}. Check WhatsApp on that phone.`);
      } else {
        setTestWaMsg(`✗ Failed: ${res.data?.error || "Unknown error"}`);
      }
    } catch (e) {
      const status = e.response?.status;
      const d = e.response?.data;
      const msg = d?.error || d?.detail || e.message;
      if (status === 404) {
        setTestWaMsg("✗ Backend not reached (404). Start backend: cd backend && uvicorn main:app --port 8000");
      } else if (status >= 500) {
        setTestWaMsg(`✗ Server error: ${msg}`);
      } else {
        setTestWaMsg(`✗ Failed: ${msg}`);
      }
    } finally {
      setTestWaLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setSuccess("");
    const parentPhone = (form.parent_phone || user?.parent_phone || "").trim();
    if (!parentPhone) {
      setErr("Parent Phone is required for WhatsApp. Add it in profile or enter below.");
      return;
    }
    setLoading(true);
    try {
      const res = await createLeave({
        reason: form.reason,
        departure_datetime: form.departure_datetime,
        arrival_datetime: form.arrival_datetime,
        parent_phone: parentPhone,
      });
      const waSent = res?.data?.whatsapp_sent;
      const waErr = res?.data?.whatsapp_error;
      setSuccess(waSent
        ? `Leave submitted! ✓ WhatsApp sent to parent (${parentPhone}). Check that phone.`
        : waErr
          ? `Leave submitted! WhatsApp failed: ${waErr} Email sent to parent instead.`
          : "Leave submitted! Email sent to parent.");
      setTimeout(() => navigate("/dashboard"), 2000);
    } catch (e) {
      const d = e.response?.data?.detail;
      const msg = typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg || x.loc?.join(".")).join(". ") : e.message || "Failed to submit leave";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="form-card">
        <h1>Submit Leave Request</h1>
        <p className="subtitle">Parent receives WhatsApp → clicks Approve/Reject → Warden receives email → Student notified via email & portal</p>
        <form onSubmit={handleSubmit}>
          <label>Leave Reason</label>
          <textarea
            placeholder="e.g. Family function, medical, etc."
            value={form.reason}
            onChange={(e) => setForm({ ...form, reason: e.target.value })}
            required
            rows={4}
          />
          <label>Departure Date & Time</label>
          <input
            type="datetime-local"
            value={form.departure_datetime}
            onChange={(e) => setForm({ ...form, departure_datetime: e.target.value })}
            required
          />
          <span className="form-hint">e.g. 15-02-2026 14:30 — click the field to pick date &amp; time</span>
          <label>Parent Phone (required – receives leave request via WhatsApp)</label>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
            <input
              type="tel"
              placeholder="e.g. 9876543210"
              value={form.parent_phone}
              onChange={(e) => setForm({ ...form, parent_phone: e.target.value })}
              required
              style={{ flex: 1, minWidth: 180 }}
            />
            <button
              type="button"
              onClick={handleTestWhatsApp}
              disabled={testWaLoading}
              className="btn btn-secondary"
              style={{ whiteSpace: "nowrap" }}
            >
              {testWaLoading ? "Sending..." : "Test WhatsApp"}
            </button>
          </div>
          {testWaMsg && <p className={testWaMsg.startsWith("✓") ? "success" : "error"} style={{ marginTop: "0.5rem" }}>{testWaMsg}</p>}
          <span className="form-hint">Parent receives leave request on WhatsApp. Parent must join Twilio sandbox first: send &quot;join row-pair&quot; to +1 415 523 8886.</span>
          <label>Arrival Date & Time</label>
          <input
            type="datetime-local"
            value={form.arrival_datetime}
            onChange={(e) => setForm({ ...form, arrival_datetime: e.target.value })}
            required
          />
          <span className="form-hint">e.g. 17-02-2026 18:00 — click the field to pick date & time</span>
          {err && <p className="error">{err}</p>}
          {success && <p className="success">{success}</p>}
          <div className="form-actions">
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? "Submitting..." : "Submit Leave"}
            </button>
            <button type="button" onClick={() => navigate("/dashboard")} className="btn btn-ghost">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
