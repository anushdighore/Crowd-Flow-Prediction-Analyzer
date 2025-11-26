import React from "react";

/**
 * TrajectoryTrackingPanel - Displays ML-annotated frame with trajectories
 * Shows bounding boxes, trajectory paths, and predicted movement
 * Used by both Webcam and External Camera pages
 */
const TrajectoryTrackingPanel = ({
  annotatedFrame,
  trackCount = 0,
  isVisible = true,
  title = "🚶 Trajectory Tracking",
}) => {
  if (!isVisible || !annotatedFrame) {
    return null;
  }

  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        padding: "1.5rem",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <h3 style={{ margin: "0 0 1rem 0" }}>{title}</h3>
      <div
        style={{
          position: "relative",
          width: "100%",
          paddingBottom: "56.25%",
          background: "#000",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        <img
          src={annotatedFrame}
          alt="Trajectory visualization with tracking"
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            objectFit: "contain",
          }}
        />

        {/* Tracking stats overlay */}
        <div
          style={{
            position: "absolute",
            top: "12px",
            left: "12px",
            background: "rgba(15,23,42,0.85)",
            color: "white",
            padding: "0.4rem 0.75rem",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "0.9rem",
            boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
          }}
        >
          🎯 Tracking: {trackCount} persons
        </div>

        {/* ML badge */}
        <div
          style={{
            position: "absolute",
            top: "12px",
            right: "12px",
            background: "rgba(16,185,129,0.9)",
            color: "white",
            padding: "0.3rem 0.6rem",
            borderRadius: "4px",
            fontSize: "0.7rem",
            fontWeight: 600,
          }}
        >
          ML Processed
        </div>
      </div>

      {/* Legend */}
      <div
        style={{
          marginTop: "1rem",
          padding: "0.75rem",
          background: "#f0fdf4",
          borderRadius: "8px",
          fontSize: "0.85rem",
          color: "#166534",
        }}
      >
        <strong>Legend:</strong> Colored circles = tracked persons • Solid lines
        = trajectory history • Dashed lines = predicted path
      </div>
    </div>
  );
};

export default TrajectoryTrackingPanel;
