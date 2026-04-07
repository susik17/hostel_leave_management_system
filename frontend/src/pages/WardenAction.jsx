import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { api } from "../api";

export default function WardenAction() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const type = searchParams.get("type");
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token || !type) {
      setStatus("error");
      setMessage("Invalid link. Missing token or action.");
      return;
    }
    if (type !== "approve" && type !== "reject") {
      setStatus("error");
      setMessage("Invalid action.");
      return;
    }
    api
      .get("/api/warden-action", { params: { token, type } })
      .then((res) => {
        // Both approve and reject are successful actions (200); only show error for actual failures
        const isError = res.data.success === false && !/rejected|approved|notified/i.test(res.data.message || "");
        if (isError) {
          setStatus("error");
          setMessage(res.data.message || "Action could not be completed.");
        } else {
          setStatus("success");
          setMessage(res.data.message || "Action completed.");
        }
      })
      .catch((e) => {
        setStatus("error");
        setMessage(e.response?.data?.message || e.response?.data?.detail || "Could not process request.");
      });
  }, [token, type]);

  return (
    <div className="page auth-page">
      <div className="auth-card result-card">
        {status === "loading" && (
          <div className="loading-wrap">
            <div className="loading-spinner" />
            <p className="loading-text">Processing...</p>
          </div>
        )}
        {status === "success" && (
          <>
            <div className="result-icon success">✓</div>
            <h1>Action Complete</h1>
            <p>{message}</p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="result-icon error">✕</div>
            <h1>Unable to Process</h1>
            <p>{["expired", "Already", "Invalid or expired", "Invalid link"].some(k => message.includes(k)) ? "This link has already been used or has expired. The leave was already processed." : message}</p>
          </>
        )}
        <Link to="/" className="btn btn-primary">Back to Home</Link>
      </div>
    </div>
  );
}
