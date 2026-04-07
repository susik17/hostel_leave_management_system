import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { getMyLeaves } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    getMyLeaves()
      .then((res) => setLeaves(res.data))
      .catch(() => setLeaves([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Poll every 10 seconds for immediate status updates
  useEffect(() => {
    const id = setInterval(refresh, 10000);
    return () => clearInterval(id);
  }, [refresh]);

  const formatDt = (d) => new Date(d).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const statusConfig = {
    PARENT_PENDING: {
      class: "status-parent-pending",
      label: "Waiting for Parent Approval",
      message: "",
    },
    WARDEN_PENDING: {
      class: "status-warden-pending",
      label: "Parent Approved – Waiting for Warden",
      message: "",
    },
    Approved: {
      class: "status-approved",
      label: "Leave Approved",
      message: "Your leave has been approved by the Warden. You may proceed to your hometown. Safe travel.",
    },
    APPROVED: {
      class: "status-approved",
      label: "Leave Approved",
      message: "Your leave has been approved by the Warden. You may proceed to your hometown. Safe travel.",
    },
    REJECTED_BY_PARENT: {
      class: "status-rejected",
      label: "Rejected by Parent",
      message: "Your parent has declined your leave request.",
    },
    REJECTED_BY_WARDEN: {
      class: "status-rejected",
      label: "Rejected by Warden",
      message: "Your leave has been rejected by the warden. Please contact hostel office.",
    },
  };

  const getStatus = (s) => statusConfig[s] || { class: "status-pending", label: s, message: "" };

  return (
    <div className="page">
      <header className="dashboard-header">
        <div>
          <h1>Student Dashboard</h1>
          <p>Welcome, {user?.name}</p>
        </div>
        <div className="header-actions">
          <Link to="/leave" className="btn btn-primary">New Leave Request</Link>
          <button onClick={logout} className="btn btn-ghost">Logout</button>
        </div>
      </header>

      <section className="leaves-section">
        <h2>My Leave Requests</h2>
        {loading ? (
          <div className="loading-wrap">
            <div className="loading-spinner" />
            <p className="loading-text">Loading leave requests...</p>
          </div>
        ) : leaves.length === 0 ? (
          <p className="empty">No leave requests yet.</p>
        ) : (
          <div className="leaves-grid">
            {leaves.map((l) => {
              const status = getStatus(l.status);
              return (
                <div key={l.id} className="leave-card">
                  <div className="leave-reason">{l.reason}</div>
                  <div className="leave-dates">
                    <span>Departure: {formatDt(l.departure_datetime)}</span>
                    <span>Arrival: {formatDt(l.arrival_datetime)}</span>
                  </div>
                  <div className="leave-status-block">
                    <span className={`status-badge ${status.class}`}>
                      {status.label}
                    </span>
                    {status.message && (
                      <p className="leave-status-message">{status.message}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
