import React from "react";
import CountDisplay from "../CountDisplay";

/**
 * StreamStats Component
 * Displays stream statistics: count, FPS, inference time, device, etc.
 */
function StreamStats({
  results,
  enableTracking,
  fps,
  frameCount,
  autoSwitch,
  autoSwitchThreshold,
  currentAutoModel,
}) {
  if (!results) return null;

  return (
    <div className="stats-panel">
      {/* Debug Panel */}
      <div
        className="stat-item"
        style={{
          background: "#fff3cd",
          borderLeft: "4px solid #ffc107",
        }}
      >
        <span className="stat-label">🐛 Debug Info:</span>
        <span className="stat-value" style={{ fontSize: "0.85em" }}>
          Tracking: {enableTracking ? "✅" : "❌"} | Tracks:{" "}
          {results.tracks ? results.tracks.length : "N/A"} | Unique:{" "}
          {results.unique_count || "N/A"}
        </span>
      </div>

      {/* Count Display Component */}
      <CountDisplay
        results={results}
        enableTracking={enableTracking}
        displayMode="stats"
        fps={fps}
        currentModel={results.model}
      />

      {/* Auto-Switch Indicator */}
      {autoSwitch && (
        <div className="stat-item auto-switch-indicator">
          <span className="stat-label">🔄 Auto-Switch:</span>
          <span className="stat-value active-model">
            {currentAutoModel.toUpperCase()}
          </span>
          <span className="threshold-info">
            (Threshold: {autoSwitchThreshold} people)
          </span>
        </div>
      )}

      {/* Performance Metrics */}
      <div className="stat-item">
        <span className="stat-label">Inference Time:</span>
        <span className="stat-value">
          {results.inference_time_ms?.toFixed(1)} ms
        </span>
      </div>

      <div className="stat-item">
        <span className="stat-label">FPS:</span>
        <span className="stat-value">{fps.toFixed(1)}</span>
      </div>

      <div className="stat-item">
        <span className="stat-label">Frames Processed:</span>
        <span className="stat-value">{frameCount}</span>
      </div>

      <div className="stat-item">
        <span className="stat-label">Device:</span>
        <span className="stat-value">{results.device}</span>
      </div>
    </div>
  );
}

export default StreamStats;
