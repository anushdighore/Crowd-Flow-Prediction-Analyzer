import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  FiX,
  FiHome,
  FiImage,
  FiVideo,
  FiCamera,
  FiMonitor,
  FiTv,
  FiUsers,
  FiChevronDown,
  FiChevronRight,
  FiBookmark,
  FiStar,
  FiSave,
  FiLogOut,
  FiMoon,
  FiSun,
} from "react-icons/fi";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";

/**
 * Menu Component
 * Daily.dev style menu with collapsible sections
 */
function Menu({ isOpen, onClose, onToggle }) {
  const location = useLocation();
  const { logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const [expandedSections, setExpandedSections] = useState({
    capture: false,
    advanced: false,
    tools: false,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const handleLogout = () => {
    logout();
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className={`menu-container ${isOpen ? "open" : ""}}`}>
      {/* Toggle Button - Always Visible in Top Right */}
      <button
        onClick={onToggle}
        className="menu-toggle-btn"
        aria-label="Toggle sidebar"
        title="Toggle menu"
      >
        <FiX />
      </button>

      {/* Menu Header - Hides when collapsed */}
      <div className="menu-header">
        <h3>Menu</h3>
      </div>

      <nav className="menu-nav">
        {/* Primary Menu Items */}
        <ul>
          <li className={isActive("/dashboard") ? "active" : ""}>
            <Link to="/dashboard" className="menu-item">
              <FiHome className="menu-icon" />
              <span>Dashboard</span>
            </Link>
          </li>
          <li className={isActive("/old-home") ? "active" : ""}>
            <Link to="/old-home" className="menu-item">
              <FiHome className="menu-icon" />
              <span>Old Home</span>
            </Link>
          </li>
          <li className={isActive("/old-dashboard") ? "active" : ""}>
            <Link to="/old-dashboard" className="menu-item">
              <FiMonitor className="menu-icon" />
              <span>Old Dashboard</span>
            </Link>
          </li>
          <li className={isActive("/image") ? "active" : ""}>
            <Link to="/image" className="menu-item">
              <FiImage className="menu-icon" />
              <span>Upload Image</span>
            </Link>
          </li>
          <li className={isActive("/video") ? "active" : ""}>
            <Link to="/video" className="menu-item">
              <FiVideo className="menu-icon" />
              <span>Upload Video</span>
            </Link>
          </li>
          <li className={isActive("/template") ? "active" : ""}>
            <Link to="/template" className="menu-item">
              <FiBookmark className="menu-icon" />
              <span>Template</span>
            </Link>
          </li>
          <li className={isActive("/template2") ? "active" : ""}>
            <Link to="/template2" className="menu-item">
              <FiBookmark className="menu-icon" />
              <span>Template 2</span>
            </Link>
          </li>
        </ul>

        {/* Capture Section */}
        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("capture")}
          >
            <span>Capture</span>
            {expandedSections.capture ? <FiChevronDown /> : <FiChevronRight />}
          </div>
          {expandedSections.capture && (
            <ul>
              <li className={isActive("/webcam") ? "active" : ""}>
                <Link to="/webcam" className="menu-item">
                  <FiCamera className="menu-icon" />
                  <span>Live Webcam</span>
                </Link>
              </li>
              <li className={isActive("/external-camera") ? "active" : ""}>
                <Link to="/external-camera" className="menu-item">
                  <FiMonitor className="menu-icon" />
                  <span>External Camera</span>
                </Link>
              </li>
              <li className={isActive("/hls") ? "active" : ""}>
                <Link to="/hls" className="menu-item">
                  <FiTv className="menu-icon" />
                  <span>HLS Streaming</span>
                </Link>
              </li>
            </ul>
          )}
        </div>

        {/* Advanced Section */}
        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("advanced")}
          >
            <span>Advanced</span>
            {expandedSections.advanced ? <FiChevronDown /> : <FiChevronRight />}
          </div>
          {expandedSections.advanced && (
            <ul>
              <li className={isActive("/pedestrian") ? "active" : ""}>
                <Link to="/pedestrian" className="menu-item">
                  <FiUsers className="menu-icon" />
                  <span>Pedestrian Tracking</span>
                </Link>
              </li>
            </ul>
          )}
        </div>

        {/* Tools Section */}
        <div className="menu-section">
          <div
            className="section-header"
            onClick={() => toggleSection("tools")}
          >
            <span>Tools</span>
            {expandedSections.tools ? <FiChevronDown /> : <FiChevronRight />}
          </div>
          {expandedSections.tools && (
            <ul>
              <li>
                <a href="#" className="menu-item">
                  <FiBookmark className="menu-icon" />
                  <span>Saved Items</span>
                </a>
              </li>
              <li>
                <a href="#" className="menu-item">
                  <FiStar className="menu-icon" />
                  <span>Favorites</span>
                </a>
              </li>
              <li>
                <a href="#" className="menu-item">
                  <FiSave className="menu-icon" />
                  <span>Archives</span>
                </a>
              </li>
            </ul>
          )}
        </div>
      </nav>

      {/* Menu Footer - Settings & Logout */}
      <div className="menu-footer">
        <button
          onClick={toggleTheme}
          className="menu-footer-btn"
          aria-label="Toggle dark mode"
          title={isDarkMode ? "Light mode" : "Dark mode"}
        >
          {isDarkMode ? <FiSun /> : <FiMoon />}
          <span>{isDarkMode ? "Light Mode" : "Dark Mode"}</span>
        </button>
        <button
          onClick={handleLogout}
          className="menu-footer-btn logout-btn"
          aria-label="Logout"
          title="Logout"
        >
          <FiLogOut />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}

export default Menu;
