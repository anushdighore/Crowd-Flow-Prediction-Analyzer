/**
 * Card Component - Reusable modular card for any content
 *
 * Props:
 * - title (string): Card header title
 * - children (ReactNode): Card content
 * - height (string): Card height (default: "450px")
 * - width (string): Card width (default: "100%")
 * - headerColor (string): Header gradient or color (default: violet gradient)
 * - showMetrics (boolean): Show metrics bar at bottom (default: false)
 * - metrics (array): Array of {label, value} objects to display
 * - showLiveStatus (boolean): Show live status badge (default: false)
 * - isLive (boolean): Live status state (default: false)
 * - className (string): Additional CSS classes
 */

import React from "react";
import "./Card.css";

function Card({
  title,
  children,
  height = "450px",
  width = "100%",
  headerColor = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  showMetrics = false,
  metrics = [],
  showLiveStatus = false,
  isLive = false,
  className = "",
}) {
  return (
    <div
      className={`modular-card ${className}`}
      style={{
        height,
        width,
      }}
    >
      {/* Card Header */}
      <div
        className="card-header"
        style={{
          background: headerColor,
        }}
      >
        <h3 className="card-title">{title}</h3>
        {showLiveStatus && (
          <div className={`live-status ${isLive ? "active" : ""}`}>
            <span className="status-indicator"></span>
            <span className="status-text">{isLive ? "LIVE" : "OFFLINE"}</span>
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="card-content">{children}</div>

      {/* Card Metrics (Optional) */}
      {showMetrics && metrics.length > 0 && (
        <div className="card-metrics">
          {metrics.map((metric, idx) => (
            <div key={idx} className="metric-item">
              <span className="metric-label">{metric.label}:</span>
              <span className="metric-value">{metric.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Card;
