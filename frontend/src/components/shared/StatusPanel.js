import React from "react";

/**
 * StatusPanel - Displays connection and streaming status
 * Used by both Webcam and External Camera pages
 */
const StatusPanel = ({
  status,
  isStreaming,
  wsState, // WebSocket readyState
  selectedModel,
  count,
  fps,
  inferenceTime,
  additionalInfo = {}, // Custom fields like webcam state, camera URL, etc.
  title = "📊 Status",
}) => {
  const getWsStatus = () => {
    switch (wsState) {
      case WebSocket.OPEN:
        return { text: "🟢 Connected", color: "#16a34a" };
      case WebSocket.CONNECTING:
        return { text: "🟡 Connecting...", color: "#ca8a04" };
      case WebSocket.CLOSING:
        return { text: "🟠 Closing...", color: "#ea580c" };
      default:
        return { text: "⚫ Disconnected", color: "#6b7280" };
    }
  };

  const wsStatus = getWsStatus();

  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#f3f4f6",
        borderRadius: "8px",
        marginBottom: "2rem",
        fontFamily: "monospace",
        fontSize: "0.9rem",
      }}
    >
      <h3 style={{ margin: "0 0 1rem 0" }}>{title}</h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "0.75rem",
        }}
      >
        <div>
          <strong>Status:</strong> {status}
        </div>
        <div>
          <strong>Streaming:</strong>{" "}
          <span style={{ color: isStreaming ? "#16a34a" : "#6b7280" }}>
            {isStreaming ? "🟢 YES" : "⚫ NO"}
          </span>
        </div>
        <div>
          <strong>WebSocket:</strong>{" "}
          <span style={{ color: wsStatus.color }}>{wsStatus.text}</span>
        </div>
        <div>
          <strong>Model:</strong> {selectedModel}
        </div>
        <div>
          <strong>Count:</strong>{" "}
          <span style={{ fontWeight: 700, color: "#667eea" }}>
            {typeof count === "number" ? count.toFixed(1) : count}
          </span>
        </div>
        <div>
          <strong>FPS:</strong>{" "}
          <span
            style={{
              color: fps > 10 ? "#16a34a" : fps > 5 ? "#ca8a04" : "#dc2626",
            }}
          >
            {fps.toFixed(1)}
          </span>
        </div>
        <div>
          <strong>Inference:</strong> {inferenceTime.toFixed(0)}ms
        </div>

        {/* Additional custom fields */}
        {Object.entries(additionalInfo).map(([key, value]) => (
          <div key={key}>
            <strong>{key}:</strong> {value}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatusPanel;
