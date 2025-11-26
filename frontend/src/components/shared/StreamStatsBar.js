import React from "react";

/**
 * StreamStatsBar - Compact stats display (Count, FPS, Inference)
 * Used by both Webcam and External Camera pages
 */
const StreamStatsBar = ({
  count,
  fps,
  inferenceTime,
  isVisible = true,
  additionalStats = [], // Array of { label, value } for custom stats
}) => {
  if (!isVisible) return null;

  const defaultStats = [
    {
      label: "Count",
      value: typeof count === "number" ? count.toFixed(0) : count,
    },
    { label: "FPS", value: fps.toFixed(1) },
    { label: "Inference", value: `${inferenceTime.toFixed(0)}ms` },
  ];

  const allStats = [...defaultStats, ...additionalStats];

  return (
    <div
      style={{
        marginTop: "1rem",
        padding: "1rem",
        background: "#f9fafb",
        borderRadius: "8px",
        display: "grid",
        gridTemplateColumns: `repeat(${allStats.length}, 1fr)`,
        gap: "1rem",
      }}
    >
      {allStats.map((stat, index) => (
        <div key={index}>
          <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
            {stat.label}
          </div>
          <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>
            {stat.value}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StreamStatsBar;
