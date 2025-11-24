import React, { useState, useEffect } from "react";

/**
 * Backend Connection Checker
 * Displays the status of backend connectivity
 */
function BackendStatus() {
  const [status, setStatus] = useState({
    health: "checking",
    yolo: "checking",
    message: "Checking backend...",
  });

  useEffect(() => {
    checkBackend();
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    try {
      // Check main health endpoint
      const healthResponse = await fetch("http://localhost:8000/health", {
        method: "GET",
      });

      if (!healthResponse.ok) {
        setStatus({
          health: "error",
          yolo: "unknown",
          message: `Backend responded with ${healthResponse.status}`,
        });
        return;
      }

      // Check YOLO endpoint
      const yoloResponse = await fetch(
        "http://localhost:8000/api/v1/yolo/health",
        {
          method: "GET",
        }
      );

      if (!yoloResponse.ok) {
        setStatus({
          health: "ok",
          yolo: "error",
          message: "Backend is running but YOLO endpoint not available",
        });
        return;
      }

      const yoloData = await yoloResponse.json();

      setStatus({
        health: "ok",
        yolo: "ok",
        message: `Backend is running. YOLO model: ${yoloData.model}`,
      });
    } catch (error) {
      setStatus({
        health: "error",
        yolo: "error",
        message: `Cannot connect to backend: ${error.message}`,
      });
    }
  };

  const getStatusColor = () => {
    if (status.health === "ok" && status.yolo === "ok") return "#4caf50";
    if (status.health === "checking") return "#ff9800";
    return "#f44336";
  };

  const getStatusIcon = () => {
    if (status.health === "ok" && status.yolo === "ok") return "✅";
    if (status.health === "checking") return "🔄";
    return "❌";
  };

  return (
    <div
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        background: "white",
        padding: "12px 16px",
        borderRadius: "8px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "14px",
        border: `2px solid ${getStatusColor()}`,
      }}
    >
      <span style={{ fontSize: "20px" }}>{getStatusIcon()}</span>
      <div>
        <div style={{ fontWeight: "600", color: getStatusColor() }}>
          Backend Status
        </div>
        <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
          {status.message}
        </div>
      </div>
      <button
        onClick={checkBackend}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          fontSize: "16px",
          padding: "4px",
        }}
        title="Refresh status"
      >
        🔄
      </button>
    </div>
  );
}

export default BackendStatus;
