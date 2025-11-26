import React from "react";

const CardWrapper = ({ children }) => (
  <div
    style={{
      background: "white",
      borderRadius: "12px",
      padding: "1.5rem",
      boxShadow: "0 10px 25px rgba(15,23,42,0.08)",
    }}
  >
    {children}
  </div>
);

const formatPoint = (point) => {
  if (!Array.isArray(point) || point.length < 2) return "--";
  const [x, y] = point;
  return `(${Math.round(x)}, ${Math.round(y)})`;
};

const TrackRow = ({ track }) => {
  const id = track?.id ?? track?.track_id ?? "Unknown";
  const speed = track?.speed?.toFixed ? `${track.speed.toFixed(2)} m/s` : "--";
  const position =
    track?.position && Array.isArray(track.position)
      ? track.position.map((value) => value?.toFixed?.(0) ?? value).join(", ")
      : "--";
  const trajectory = Array.isArray(track?.trajectory) ? track.trajectory : [];
  const startPoint = trajectory.length ? formatPoint(trajectory[0]) : "--";
  const endPoint = trajectory.length
    ? formatPoint(trajectory[trajectory.length - 1])
    : "--";

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "80px 1.2fr 1.3fr 120px",
        gap: "0.5rem",
        fontSize: "0.9rem",
        padding: "0.35rem 0",
        borderBottom: "1px solid #f1f5f9",
      }}
    >
      <span style={{ fontWeight: 600 }}>#{id}</span>
      <span style={{ color: "#475569" }}>{position}</span>
      <span style={{ color: "#0369a1", fontWeight: 600 }}>
        {startPoint} → {endPoint}
      </span>
      <span style={{ color: "#0f172a", fontWeight: 600 }}>{speed}</span>
    </div>
  );
};

const WebcamTrajectoryPanel = ({ isActive, tracks = [], uniqueCount = 0 }) => {
  if (!isActive) {
    return (
      <CardWrapper>
        <h3 style={{ marginTop: 0 }}>🧭 Trajectory window</h3>
        <p style={{ color: "#64748b", marginBottom: 0 }}>
          Switch to YOLOv8, enable tracking, and allow a few frames for
          detections to lock before trajectories become visible.
        </p>
      </CardWrapper>
    );
  }

  const hasTracks = Array.isArray(tracks) && tracks.length > 0;

  return (
    <CardWrapper>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <p
            style={{
              fontSize: "0.8rem",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "#94a3b8",
              margin: 0,
            }}
          >
            Trajectory window
          </p>
          <h3 style={{ margin: "0.25rem 0 0" }}>Live YOLO tracking</h3>
        </div>
        <div
          style={{
            background: "rgba(34,197,94,0.15)",
            color: "#15803d",
            padding: "0.35rem 0.85rem",
            borderRadius: "999px",
            fontWeight: 600,
          }}
        >
          Unique IDs: {uniqueCount ?? "--"}
        </div>
      </header>

      {hasTracks ? (
        <div style={{ marginTop: "1rem" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "80px 1.2fr 1.3fr 120px",
              fontSize: "0.75rem",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "#94a3b8",
              paddingBottom: "0.35rem",
              borderBottom: "1px solid #e2e8f0",
            }}
          >
            <span>ID</span>
            <span>Current Position</span>
            <span>Path (A → B)</span>
            <span>Speed</span>
          </div>
          {tracks.slice(0, 5).map((track, index) => (
            <TrackRow
              key={`${track?.id ?? track?.track_id ?? "track"}-${index}`}
              track={track}
            />
          ))}
          {tracks.length > 5 && (
            <p style={{ marginTop: "0.75rem", color: "#94a3b8" }}>
              +{tracks.length - 5} additional tracks hidden
            </p>
          )}
        </div>
      ) : (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            background: "#ecfeff",
            borderRadius: "10px",
            color: "#0f172a",
          }}
        >
          Waiting for tracker data from backend...
        </div>
      )}
    </CardWrapper>
  );
};

export default WebcamTrajectoryPanel;
