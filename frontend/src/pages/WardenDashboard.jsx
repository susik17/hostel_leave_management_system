import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { getAllLeaves, wardenApprove, wardenReject, wardenDateStats } from "../api";
import { useAuth } from "../context/AuthContext";

export default function WardenDashboard() {
  const { user, logout } = useAuth();
  const [leaves, setLeaves] = useState([]);
  const [filter, setFilter] = useState("warden_pending");
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(null);
  const [searchDate, setSearchDate] = useState("");
  const [dateStats, setDateStats] = useState(null);
  const [dateStatsLoading, setDateStatsLoading] = useState(false);

  const refresh = useCallback(() => {
    setLoading(true);
    getAllLeaves(filter || undefined)
      .then((res) => setLeaves(res.data))
      .catch(() => setLeaves([]))
      .finally(() => setLoading(false));
  }, [filter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const interval = setInterval(refresh, 10000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleDateSearch = () => {
    if (!searchDate.trim()) return;
    setDateStatsLoading(true);
    setDateStats(null);
    wardenDateStats(searchDate.trim())
      .then((res) => setDateStats(res.data))
      .catch((e) => {
        setDateStats(null);
        alert(e.response?.data?.detail || "Invalid date");
      })
      .finally(() => setDateStatsLoading(false));
  };

  const handleApprove = (id) => {
    setActing(id);
    wardenApprove(id)
      .then(() => refresh())
      .catch((e) => alert(e.response?.data?.detail || "Failed"))
      .finally(() => setActing(null));
  };

  const handleReject = (id) => {
    setActing(id);
    wardenReject(id)
      .then(() => refresh())
      .catch((e) => alert(e.response?.data?.detail || "Failed"))
      .finally(() => setActing(null));
  };

  const formatDt = (d) => new Date(d).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const formatDepArr = (d) => new Date(d).getDate();

  const shortDateDisplay = (dep, arr, name) =>
    `${formatDepArr(dep)}/ ${name} --> ${formatDepArr(arr)}/`;

  const statusClass = (s) => {
    if (s === "Approved") return "status-approved";
    if (s === "REJECTED_BY_WARDEN" || s === "REJECTED_BY_PARENT" || s === "Rejected") return "status-rejected";
    return "status-pending";
  };

  const canWardenAct = (l) =>
    (l.status === "WARDEN_PENDING" || (l.status === "Pending" && l.parent_verified));

  return (
    <div className="page">
      <header className="dashboard-header">
        <div>
          <h1>Warden Dashboard</h1>
          <p>Welcome, {user?.name}</p>
        </div>
        <button onClick={logout} className="btn btn-ghost">Logout</button>
      </header>

      <section className="warden-section">
        <div className="date-search-bar">
          <h3>Search by date</h3>
          <div className="date-search-row">
            <input
              type="text"
              placeholder="Enter date: 18 or 18-02-2026"
              value={searchDate}
              onChange={(e) => setSearchDate(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleDateSearch()}
            />
            <button className="btn btn-primary" onClick={handleDateSearch} disabled={dateStatsLoading}>
              {dateStatsLoading ? "..." : "Search"}
            </button>
          </div>
          {dateStats && (
            <div className="date-stats-box">
              <p><strong>Date:</strong> {dateStats.date}</p>
              <p><strong>Away (on leave):</strong> <em>{dateStats.away}</em></p>
              <p><strong>Remaining (in hostel):</strong> <em>{dateStats.remaining}</em></p>
              <p><strong>Food count:</strong> {dateStats.food_count} (meals to prepare)</p>
            </div>
          )}
        </div>

        <div className="filter-bar">
          <span>Filter:</span>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All</option>
            <option value="warden_pending">Warden Pending</option>
            <option value="parent_pending">Parent Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected_by_warden">Rejected by Warden</option>
            <option value="rejected_by_parent">Rejected by Parent</option>
          </select>
        </div>

        {loading ? (
          <div className="loading-wrap">
            <div className="loading-spinner" />
            <p className="loading-text">Loading requests...</p>
          </div>
        ) : leaves.length === 0 ? (
          <p className="empty">No leave requests.</p>
        ) : (
          <div className="table-wrap">
            <table className="leaves-table">
              <thead>
                <tr>
                  <th>Dept / Date (Dep → Arr)</th>
                  <th>Reason</th>
                  <th>Full Departure</th>
                  <th>Full Arrival</th>
                  <th>Parent</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {leaves.map((l) => (
                  <tr key={l.id}>
                    <td>
                      <div className="dep-arr-short">{shortDateDisplay(l.departure_datetime, l.arrival_datetime, l.student_name)}</div>
                      <div className="dept-label">{l.department}</div>
                    </td>
                    <td>{l.reason}</td>
                    <td>{formatDt(l.departure_datetime)}</td>
                    <td>{formatDt(l.arrival_datetime)}</td>
                    <td>
                      {l.parent_verified ? (
                        <span className="status-badge status-approved">Approved</span>
                      ) : (
                        <span className="status-badge status-pending">Pending</span>
                      )}
                    </td>
                    <td>
                      <span className={`status-badge ${statusClass(l.status)}`}>
                        {l.status === "WARDEN_PENDING" ? "Parent Approved" : l.status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td>
                      {canWardenAct(l) && (
                        <div className="action-buttons">
                          <button
                            className="btn btn-sm btn-approve"
                            onClick={() => handleApprove(l.id)}
                            disabled={acting === l.id}
                          >
                            {acting === l.id ? "..." : "Approve Leave"}
                          </button>
                          <button
                            className="btn btn-sm btn-reject"
                            onClick={() => handleReject(l.id)}
                            disabled={acting === l.id}
                          >
                            Reject Leave
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
