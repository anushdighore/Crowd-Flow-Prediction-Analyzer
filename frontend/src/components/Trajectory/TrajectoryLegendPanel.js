import React from "react";

// Generate distinct colors for each track ID (same as TrajectoryVisualizationFrame)
const getColorForId = (id) => {
  const numericId =
    typeof id === "number"
      ? id
      : parseInt(String(id).replace(/\D/g, ""), 10) || 0;
  const hue = (numericId * 137.508) % 360;
  return `hsl(${hue}, 85%, 50%)`;
};

const formatDistance = (pixels, pixelsPerMeter = 50) => {
  const meters = pixels / pixelsPerMeter;
  if (meters < 1) {
    return `${Math.round(meters * 1000)} mm`;
  }
  return `${meters.toFixed(2)} m`;
};

const TrackLegendItem = ({ track }) => {
  const id = track?.id ?? track?.track_id ?? 0;
  const color = getColorForId(id);
  const trajectory = track?.trajectory || [];
  const speed = track?.speed || 0;
  const state = track?.state ?? -1;
  const stateLabels = ["New", "Tracked", "Lost"];

  // Calculate total distance traveled
  let totalDistance = 0;
  for (let i = 1; i < trajectory.length; i++) {
    const dx = trajectory[i][0] - trajectory[i - 1][0];
    const dy = trajectory[i][1] - trajectory[i - 1][1];
    totalDistance += Math.sqrt(dx * dx + dy * dy);
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        padding: "0.75rem 1rem",
        background: "#f8fafc",
        borderRadius: "8px",
        borderLeft: `4px solid ${color}`,
      }}
    >
      <div
        style={{
          width: "12px",
          height: "12px",
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 8px ${color}`,
        }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>Person #{id}</div>
        <div
          style={{
            fontSize: "0.8rem",
            color: "#64748b",
            display: "flex",
            gap: "1rem",
            marginTop: "0.25rem",
          }}
        >
          <span>📍 {trajectory.length} points</span>
          <span>📏 {formatDistance(totalDistance)}</span>
          {speed > 0 && <span>🏃 {speed.toFixed(1)} m/s</span>}
        </div>
      </div>
      <div
        style={{
          padding: "0.25rem 0.5rem",
          borderRadius: "4px",
          fontSize: "0.75rem",
          fontWeight: 600,
          background:
            state === 1 ? "#dcfce7" : state === 0 ? "#fef3c7" : "#fee2e2",
          color: state === 1 ? "#166534" : state === 0 ? "#92400e" : "#991b1b",
        }}
      >
        {stateLabels[state] || "Unknown"}
      </div>
    </div>
  );
};

const TrajectoryLegendPanel = ({ tracks = [], isActive = false }) => {
  if (!isActive) {
    return (
      <div
        style={{
          background: "white",
          borderRadius: "12px",
          padding: "1.5rem",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        <h3 style={{ margin: "0 0 0.5rem 0" }}>🎨 Path Legend</h3>
        <p style={{ color: "#64748b", margin: 0 }}>
          Enable YOLOv8 + Tracking to see individual path colors
        </p>
      </div>
    );
  }

  const activeTracks = tracks.filter((t) => t?.trajectory?.length > 0);

  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        padding: "1.5rem",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <h3 style={{ margin: 0 }}>🎨 Path Legend</h3>
        <span
          style={{
            padding: "0.25rem 0.75rem",
            background: "#e0e7ff",
            color: "#4338ca",
            borderRadius: "999px",
            fontSize: "0.85rem",
            fontWeight: 600,
          }}
        >
          {activeTracks.length} active
        </span>
      </div>

      {activeTracks.length === 0 ? (
        <div
          style={{
            padding: "1.5rem",
            background: "#f0f9ff",
            borderRadius: "8px",
            textAlign: "center",
            color: "#0369a1",
          }}
        >
          <p style={{ margin: 0, fontSize: "0.9rem" }}>
            Waiting for people to be detected...
          </p>
          <p
            style={{
              margin: "0.5rem 0 0",
              fontSize: "0.8rem",
              color: "#64748b",
            }}
          >
            Each person will get a unique colored path
          </p>
        </div>
      ) : (
        <div
          style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}
        >
          {activeTracks.slice(0, 8).map((track, idx) => (
            <TrackLegendItem
              key={track?.id ?? track?.track_id ?? idx}
              track={track}
            />
          ))}
          {activeTracks.length > 8 && (
            <p
              style={{
                margin: "0.5rem 0 0",
                color: "#64748b",
                fontSize: "0.85rem",
                textAlign: "center",
              }}
            >
              +{activeTracks.length - 8} more people tracked
            </p>
          )}
        </div>
      )}

      {/* Color legend explanation */}
      <div
        style={{
          marginTop: "1rem",
          padding: "0.75rem",
          background: "#f1f5f9",
          borderRadius: "6px",
          fontSize: "0.8rem",
          color: "#475569",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginBottom: "0.5rem",
          }}
        >
          <div
            style={{
              width: "24px",
              height: "3px",
              background:
                "linear-gradient(to right, rgba(99,102,241,0.3), #6366f1)",
            }}
          />
          <span>Solid line = Path traveled</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <div
            style={{
              width: "24px",
              height: "3px",
              background:
                "repeating-linear-gradient(to right, #818cf8, #818cf8 4px, transparent 4px, transparent 8px)",
            }}
          />
          <span>Dashed line = Predicted path</span>
        </div>
      </div>
    </div>
  );
};

export default TrajectoryLegendPanel;
