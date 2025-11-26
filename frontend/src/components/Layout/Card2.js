/**
 * Card2 Component - Spanning card with children support
 *
 * Similar to the feature cards in template2.js, this component creates
 * spanning cards that can contain any children content.
 *
 * Props:
 * - icon (string): Emoji or icon to display (e.g., "📤")
 * - title (string): Card title
 * - description (string): Card description
 * - color (string): Border and hover color (hex code)
 * - children (ReactNode): Card content
 * - onClick (function): Click handler
 * - className (string): Additional CSS classes
 * - linkTo (string): Navigation link (optional)
 */

import React from "react";
import { Link } from "react-router-dom";
import "./Card.css";

function Card2({
  icon,
  title,
  description,
  color = "#667eea",
  children,
  onClick,
  className = "",
  linkTo = null,
}) {
  const cardContent = (
    <div
      className={`spanning-card ${className}`}
      style={{
        textDecoration: "none",
        background: "white",
        borderRadius: "12px",
        padding: "1.5rem",
        border: "2px solid rgba(102, 126, 234, 0.15)",
        transition: "all 0.3s ease",
        cursor: "pointer",
        display: "block",
        minHeight: "300px",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)";
        e.currentTarget.style.borderColor = color;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = "none";
        e.currentTarget.style.borderColor = "rgba(102, 126, 234, 0.15)";
      }}
      onClick={onClick}
    >
      {/* Card Header with Icon and Title */}
      {icon && (
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>{icon}</div>
      )}

      {title && (
        <h3
          style={{
            fontSize: "1.25rem",
            marginBottom: "0.5rem",
            color: "#333",
          }}
        >
          {title}
        </h3>
      )}

      {description && (
        <p style={{ color: "#666", lineHeight: "1.6", margin: "0 0 1.5rem 0" }}>
          {description}
        </p>
      )}

      {/* Card Children Content */}
      {children && <div style={{ marginTop: "1rem" }}>{children}</div>}
    </div>
  );

  // If linkTo is provided, wrap in Link, otherwise return the div
  if (linkTo) {
    return (
      <Link to={linkTo} style={{ textDecoration: "none" }}>
        {cardContent}
      </Link>
    );
  }

  return cardContent;
}

export default Card2;
