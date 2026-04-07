import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { api } from "../api";

export default function ParentAction() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const type = searchParams.get("type");
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  const [preview, setPreview] = useState(null);

  // Token only, no type: show Approve/Reject choice buttons
  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid link. Missing token.");
      return;
    }
    if (type) {
      // type=approve or type=reject: process action
      api
        .get("/api/parent-action", { params: { token, type } })
        .then((res) => {
          if (res.data.success) {
            setStatus("success");
            setMessage(res.data.message || "Request confirmed. Warden will get email shortly.");
          } else {
            setStatus("error");
            setMessage(res.data.message || "Request rejected or already processed.");
          }
        })
        .catch((e) => {
          setStatus("error");
          setMessage(e.response?.data?.message || e.response?.data?.detail || "Could not process request.");
        });
      return;
    }
    // No type: fetch preview and show choice buttons
    api
      .get("/api/leave-preview", { params: { token } })
      .then((res) => {
        if (res.data.valid) {
          setPreview(res.data);
          setStatus("choice");
        } else {
          setStatus("error");
          setMessage(res.data.message || "Invalid or expired link.");
        }
      })
      .catch(() => {
        setStatus("error");
        setMessage("Could not load request.");
      });
  }, [token, type]);

  return (
    <div className="page auth-page">
      <div className="auth-card result-card">
        {status === "loading" && (
          <div className="loading-wrap">
            <div className="loading-spinner" />
            <p className="loading-text">Loading...</p>
          </div>
        )}
        {status === "choice" && preview && (
          <>
            <h1>Hostel Leave Request</h1>
            <p>Your child <strong>{preview.student_name}</strong> ({preview.department}) has requested hostel leave.</p>
            <table style={{ width: "100%", margin: "1rem 0", fontSize: "0.95rem" }}>
              <tbody>
                <tr><td><b>Reason:</b></td><td>{preview.reason}</td></tr>
                <tr><td><b>Departure:</b></td><td>{preview.departure}</td></tr>
                <tr><td><b>Arrival:</b></td><td>{preview.arrival}</td></tr>
              </tbody>
            </table>
            <p style={{ marginBottom: "1rem" }}>Tap a button below. Warden gets email when you approve.</p>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}>
              <Link
                to={`/parent-action?token=${token}&type=approve`}
                className="btn btn-primary"
                style={{ background: "#22c55e", minWidth: "140px" }}
              >
                Approve
              </Link>
              <Link
                to={`/parent-action?token=${token}&type=reject`}
                className="btn"
                style={{ background: "#ef4444", color: "white", minWidth: "140px" }}
              >
                Reject
              </Link>
            </div>
          </>
        )}
        {status === "success" && (
          <>
            <div className="result-icon success">✓</div>
            <h1>Leave Confirmed</h1>
            <p>{message}</p>
            <p className="form-hint" style={{ marginTop: "0.5rem" }}>Warden has been notified by email.</p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="result-icon error">✕</div>
            <h1>Request Closed</h1>
            <p>{message === "Already used" || message === "Link expired" ? "This link has already been used or has expired. The request was already processed." : message}</p>
          </>
        )}
        <Link to="/" className="btn btn-primary" style={{ marginTop: "1rem" }}>Back to Home</Link>
      </div>
    </div>
  );
}
