import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { verifyParentToken } from "../api";

export default function Verify() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid link. No token provided.");
      return;
    }
    verifyParentToken(token)
      .then((res) => {
        if (res.data.success) {
          setStatus("success");
          setMessage(res.data.message || "Request verified. Warden will approve shortly.");
        } else {
          setStatus("error");
          setMessage(res.data.message || "Something went wrong.");
        }
      })
      .catch(() => {
        setStatus("error");
        setMessage("Could not process request.");
      });
  }, [token]);

  return (
    <div className="page auth-page">
      <div className="auth-card result-card">
        {status === "loading" && (
          <div className="loading-wrap">
            <div className="loading-spinner" />
            <p className="loading-text">Verifying...</p>
          </div>
        )}
        {status === "success" && (
          <>
            <div className="result-icon success">✓</div>
            <h1>Request Verified</h1>
            <p>{message}</p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="result-icon error">✕</div>
            <h1>Unable to Verify</h1>
            <p>{message}</p>
          </>
        )}
        <Link to="/" className="btn btn-primary">Back to Home</Link>
      </div>
    </div>
  );
}
