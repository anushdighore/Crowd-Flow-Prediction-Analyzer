import React from "react";

/**
 * CountDisplay Component
 *
 * Displays crowd count statistics in a reusable format.
 * Shows exact count (integer), decimal accuracy, and unique tracks (when tracking enabled).
 *
 * @param {Object} props - Component props
 * @param {Object} props.results - Prediction results object
 * @param {number} props.results.count - Current count
 * @param {number} props.results.raw_count - Raw count with decimal precision (optional)
 * @param {number} props.results.unique_count - Unique track count (when tracking enabled)
 * @param {boolean} props.enableTracking - Whether tracking is enabled
 * @param {string} props.displayMode - 'overlay' (on video) or 'stats' (detailed panel)
 * @param {number} props.fps - Frames per second (optional, for overlay mode)
 * @param {string} props.currentModel - Current model name (optional)
 * @param {boolean} props.autoSwitch - Whether auto-switch is enabled (optional)
 */
export default function CountDisplay({
  results,
  enableTracking,
  displayMode = "stats",
  fps,
  currentModel,
  autoSwitch,
}) {
  // Don't render if no results
  if (!results) {
    return null;
  }

  // Overlay mode (displayed on top of video feed)
  if (displayMode === "overlay") {
    return (
      <div className="video-overlay">
        <div className="count-badge">
          <span className="count-label">Count:</span>
          <span className="count-value">{Math.round(results.count)}</span>
        </div>

        {fps !== undefined && (
          <div className="fps-badge">
            <span className="fps-value">{fps.toFixed(1)} FPS</span>
          </div>
        )}

        {autoSwitch && currentModel && (
          <div className="auto-model-badge">
            <span className="auto-model-label">
              🔄 {currentModel.toUpperCase()}
            </span>
          </div>
        )}

        {enableTracking && results.unique_count !== undefined && (
          <div className="tracking-badge">
            <span className="tracking-label">Unique:</span>
            <span className="tracking-value">{results.unique_count}</span>
          </div>
        )}
      </div>
    );
  }

  // Stats mode (detailed statistics panel)
  if (displayMode === "stats") {
    return (
      <div className="count-statistics">
        {/* Exact Count (Integer) */}
        <div className="stat-item count-display-stat">
          <span className="stat-label">👥 People Count (Exact):</span>
          <span className="stat-value count-exact">
            {Math.round(results.count)}
          </span>
        </div>

        {/* Decimal Accuracy Count */}
        <div className="stat-item count-display-stat">
          <span className="stat-label">📊 Count (Decimal Accuracy):</span>
          <span className="stat-value count-decimal">
            {typeof results.raw_count !== "undefined"
              ? results.raw_count.toFixed(2)
              : results.count.toFixed(2)}
          </span>
        </div>

        {/* Unique Tracks (when tracking enabled) */}
        {enableTracking && results.unique_count !== undefined && (
          <div className="stat-item">
            <span className="stat-label">🎯 Unique Tracks:</span>
            <span className="stat-value">{results.unique_count}</span>
          </div>
        )}

        {/* FPS (if provided) */}
        {fps !== undefined && (
          <div className="stat-item">
            <span className="stat-label">⚡ FPS:</span>
            <span className="stat-value">{fps.toFixed(1)}</span>
          </div>
        )}

        {/* Model (if provided) */}
        {currentModel && (
          <div className="stat-item">
            <span className="stat-label">🤖 Model:</span>
            <span className="stat-value">{currentModel.toUpperCase()}</span>
          </div>
        )}
      </div>
    );
  }

  // Compact mode (single-line display)
  if (displayMode === "compact") {
    return (
      <div className="count-compact">
        <span className="count-icon">👥</span>
        <span className="count-value-large">{Math.round(results.count)}</span>
        {enableTracking && results.unique_count !== undefined && (
          <>
            <span className="count-separator">|</span>
            <span className="count-label-small">Unique:</span>
            <span className="count-value-small">{results.unique_count}</span>
          </>
        )}
      </div>
    );
  }

  return null;
}
