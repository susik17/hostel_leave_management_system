import axios from "axios";

// Use relative URL so Vite proxy sends /api/* to backend
const API_BASE = "";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 500) {
      console.error("[500 Error]", err.response?.data?.detail);
      if (err.response?.data?.traceback) {
        console.error("Traceback:", err.response.data.traceback);
      }
    }
    return Promise.reject(err);
  }
);

export const register = (data) => api.post("/api/register", data);
export const login = (data) => api.post("/api/login", data);
export const getMe = () => api.get("/api/me");
export const createLeave = (data) => api.post("/api/leave", data);
export const getMyLeaves = () => api.get("/api/leave/my");
export const getAllLeaves = (statusFilter) =>
  api.get("/api/leave/all", {
    params: statusFilter ? { status_filter: statusFilter } : {},
  });
export const verifyParentToken = (token) =>
  api.get(`/api/verify?token=${token}`);
export const wardenApprove = (leaveId) =>
  api.post(`/api/leave/${leaveId}/approve`);
export const wardenReject = (leaveId) =>
  api.post(`/api/leave/${leaveId}/reject`);
export const wardenDateStats = (searchDate) =>
  api.get("/api/warden/date-stats", { params: { search_date: searchDate } });
// Test WhatsApp: call backend directly (proxy sometimes returns 404 when backend restarts)
const BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const testWhatsApp = (to) => {
  if (!to) throw new Error("Phone number required");
  const url = `${BACKEND_URL}/api/test-whatsapp?to=${encodeURIComponent(to)}`;
  return axios.get(url, { headers: { "Content-Type": "application/json" } });
};
