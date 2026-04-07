import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LeaveForm from "./pages/LeaveForm";
import WardenDashboard from "./pages/WardenDashboard";
import Verify from "./pages/Verify";
import ParentAction from "./pages/ParentAction";
import WardenAction from "./pages/WardenAction";

function ProtectedStudent({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page"><p>Loading...</p></div>;
  if (!user) return <Navigate to="/login" />;
  if (user.role === "warden") return <Navigate to="/warden" />;
  return children;
}

function ProtectedWarden({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page"><p>Loading...</p></div>;
  if (!user) return <Navigate to="/login" />;
  if (user.role !== "warden") return <Navigate to="/dashboard" />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/verify" element={<Verify />} />
      <Route path="/parent-action" element={<ParentAction />} />
      <Route path="/warden-action" element={<WardenAction />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedStudent>
            <Dashboard />
          </ProtectedStudent>
        }
      />
      <Route
        path="/leave"
        element={
          <ProtectedStudent>
            <LeaveForm />
          </ProtectedStudent>
        }
      />
      <Route
        path="/warden"
        element={
          <ProtectedWarden>
            <WardenDashboard />
          </ProtectedWarden>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
