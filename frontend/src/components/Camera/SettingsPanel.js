import React from "react";

/**
 * SettingsPanel Component
 * Handles visualization settings: heatmap, tracking, and other options
 */
function SettingsPanel({
  enableHeatmap,
  onEnableHeatmapChange,
  enableTracking,
  onEnableTrackingChange,
  isStreaming,
}) {
  return (
    <div className="settings-panel">
      <h4>⚙️ Visualization Settings</h4>

      {/* Heatmap Toggle */}
      <div className="setting-item">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={enableHeatmap}
            onChange={(e) => onEnableHeatmapChange(e.target.checked)}
            disabled={isStreaming}
          />
          🔥 Show Heatmap/Detection Overlay
        </label>
      </div>

      {/* Tracking Toggle */}
      <div className="setting-item">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={enableTracking}
            onChange={(e) => onEnableTrackingChange(e.target.checked)}
            disabled={isStreaming}
          />
          🎯 Enable Trajectory Visualization (YOLO only)
        </label>
        {enableTracking && (
          <p className="setting-hint">
            Shows colored paths (🔴 NEW, 🟢 TRACKED, 🟡 LOST) and track IDs
          </p>
        )}
      </div>
    </div>
  );
}

export default SettingsPanel;
