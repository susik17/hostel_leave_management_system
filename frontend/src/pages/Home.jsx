import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page home-page">
      <nav className="home-nav">
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>
      <div className="hero">
        <h1>Hostel Leave Approval</h1>
        <p>Submit leave requests. Parent approves via secure email, then warden gives final approval. Simple & traceable.</p>
        <div className="hero-actions">
          <Link to="/register" className="btn btn-primary">Get Started</Link>
          <Link to="/login" className="btn btn-secondary">Login</Link>
        </div>
      </div>
    </div>
  );
}
