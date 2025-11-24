import { useAuth } from "../../context/AuthContext";
import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { FiSearch } from "react-icons/fi";

const Nav = ({ mode, setMode }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState("");

  if (!isAuthenticated) {
    return null;
  }

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      console.log("Search query:", searchQuery);
      // Add search functionality here
    }
  };

  return (
    <>
      <nav className="github-navbar">
        <div className="nav-container">
          {/* Left: Logo (Hamburger removed - now in Menu) */}
          <div className="nav-left">
            {/* Logo and Title */}
            <div className="nav-brand">
              <span className="brand-icon">🧠</span>
              <Link to="/" className="brand-text">
                Crowd Analysis
              </Link>
            </div>
          </div>

          {/* Center: Search Bar */}
          <div className="nav-center">
            <form className="search-form" onSubmit={handleSearch}>
              <FiSearch className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search features, docs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>

          {/* Right: User Menu */}
          <div className="nav-right">
            <div className="user-info">
              <span className="user-avatar">
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </span>
              <span className="user-name">{user?.username}</span>
            </div>
            <button className="logout-btn" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Nav;
