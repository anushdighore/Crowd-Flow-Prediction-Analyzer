/**
 * CSRNetCard Component - Modular CSRNet Crowd Counter Card
 *
 * Reusable component that can be integrated into:
 * - Webcam page
 * - External Camera page
 * - Image upload page
 *
 * Props:
 * - results (object): Results from CSRNet API (count, heatmap, image_size, filename, density_map_shape, inference_time_ms)
 * - previewUrl (string): Preview URL of the image
 * - loading (boolean): Loading state
 * - error (string): Error message
 * - onClear (function): Callback to clear the card state
 * - title (string): Card title (default: "CSRNet Crowd Counter")
 * - showRawJson (boolean): Whether to show raw JSON response (default: true)
 * - showHeatmap (boolean): Whether to show heatmap card below (default: true)
 */

import React, { useMemo } from "react";
import HeatmapCard from "./HeatmapCard";
import "./CSRNetCard.css";

const normaliseCount = (payload) => {
  if (!payload) return null;
  const candidates = [payload.count, payload.crowd_count, payload.people];
  for (const value of candidates) {
    if (typeof value === "number" && Number.isFinite(value)) {
      return Math.round(value);
    }
    if (typeof value === "string") {
      const parsed = Number(value);
      if (!Number.isNaN(parsed)) {
        return Math.round(parsed);
      }
    }
  }
  return null;
};

function CSRNetCard({
  results,
  previewUrl,
  loading = false,
  error = null,
  onClear = null,
  title = "CSRNet Crowd Counter",
  showRawJson = true,
  showHeatmap = true,
}) {
  const displayCount = useMemo(() => normaliseCount(results), [results]);

  // Don't render if no results and not loading or error
  if (!results && !loading && !error) {
    return null;
  }

  return (
    <div className="csrnet-card-container">
      {/* Results Display */}
      {results && (
        <div className="csrnet-results-section">
          <div className="results-header">
            <h3 className="results-title">✅ Crowd Count Results</h3>
          </div>

          <div className="results-content">
            <div className="count-display">
              <div className="count-number">
                {displayCount !== null ? displayCount : "—"}
              </div>
              <div className="count-label-text">People Detected</div>
            </div>

            <div className="results-details">
              <div className="detail-row">
                <span className="detail-label">Image Size:</span>
                <span className="detail-value">{results.image_size}</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Filename:</span>
                <span className="detail-value">{results.filename}</span>
              </div>

              {results.density_map_shape && (
                <div className="detail-row">
                  <span className="detail-label">Density Map Shape:</span>
                  <span className="detail-value">
                    {results.density_map_shape.join(" x ")}
                  </span>
                </div>
              )}

              {results.inference_time_ms && (
                <div className="detail-row">
                  <span className="detail-label">Inference Time:</span>
                  <span className="detail-value">
                    {results.inference_time_ms.toFixed(2)} ms
                  </span>
                </div>
              )}
            </div>

            {showRawJson && (
              <details className="json-details">
                <summary className="json-summary">
                  View Raw JSON Response
                </summary>
                <pre className="json-content">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </details>
            )}

            {onClear && (
              <button className="csrnet-clear-btn" onClick={onClear}>
                Clear Results
              </button>
            )}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="csrnet-loading-section">
          <div className="loading-spinner"></div>
          <p className="loading-text">Processing image...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="csrnet-error-section">
          <p className="error-icon">⚠️</p>
          <p className="error-message">{error}</p>
        </div>
      )}

      {/* Heatmap Card */}
      {showHeatmap && results && (
        <div className="csrnet-heatmap-section">
          <HeatmapCard
            heatmapImage={results.heatmap}
            originalImage={previewUrl}
            count={displayCount}
            inferenceTime={results.inference_time_ms}
            isLoading={loading}
            error={error}
            title="CSRNet Density Heatmap"
            showOriginalImage={true}
          />
        </div>
      )}
    </div>
  );
}

export default CSRNetCard;
