/**
 * HeatmapCard Component - CSRNet Density Map Heatmap Display
 *
 * Modular component for displaying density heatmap from CSRNet model.
 * Can be used across different pages (Image upload, Webcam, External Camera, etc.)
 *
 * Props:
 * - heatmapImage (string): Base64 encoded heatmap image from backend (data:image/jpeg;base64,...)
 * - originalImage (string): Base64 encoded original image for reference
 * - count (number): Crowd count from CSRNet
 * - inferenceTime (number): Inference time in milliseconds
 * - isLoading (boolean): Whether currently processing
 * - error (string): Error message if any
 * - title (string): Card title
 * - showOriginalImage (boolean): Whether to show original image alongside heatmap
 */

import React from "react";
import "./HeatmapCard.css";

export default function HeatmapCard({
  heatmapImage,
  originalImage,
  count,
  inferenceTime,
  isLoading = false,
  error = null,
  title = "CSRNet Density Heatmap",
  showOriginalImage = false,
  enableHeatmap = true, // NEW: Flag to check if heatmap should be expected
  selectedModel = "CSRNet", // NEW: Current model to determine if heatmap is applicable
}) {
  // Enhanced conditional rendering - show waiting state if heatmap expected
  if (!heatmapImage && !isLoading && !error) {
    // Density models that support heatmaps
    const densityModels = ["CSRNet", "MCNN", "VMamba"];

    // Show "waiting" message if heatmap is enabled and using a density model
    if (enableHeatmap && densityModels.includes(selectedModel)) {
      return (
        <div className="csrnet-heatmap-card">
          <div className="heatmap-card-header">
            <h3 className="heatmap-card-title">🔥 {title}</h3>
          </div>
          <div className="heatmap-card-content">
            <div className="heatmap-loading">
              <div className="loading-spinner"></div>
              <p>⏳ Waiting for heatmap data...</p>
              <p
                style={{
                  fontSize: "0.85rem",
                  color: "#666",
                  marginTop: "0.5rem",
                }}
              >
                Make sure "Enable Heatmap" is ON and using a density model
                (CSRNet/MCNN/VMamba)
              </p>
            </div>
          </div>
        </div>
      );
    }

    // Don't render for YOLO or when heatmap disabled
    return null;
  }

  return (
    <div className="csrnet-heatmap-card">
      <div className="heatmap-card-header">
        <h3 className="heatmap-card-title">🔥 {title}</h3>
        {count !== undefined && count !== null && (
          <div className="heatmap-card-count">
            <span className="count-label">Detected:</span>
            <span className="count-value">{Math.round(count)}</span>
          </div>
        )}
      </div>

      <div className="heatmap-card-content">
        {error && (
          <div className="heatmap-error">
            <p className="error-icon">⚠️</p>
            <p className="error-text">{error}</p>
          </div>
        )}

        {isLoading && (
          <div className="heatmap-loading">
            <div className="loading-spinner"></div>
            <p>Generating heatmap...</p>
          </div>
        )}

        {heatmapImage && !isLoading && (
          <div className="heatmap-display-container">
            {showOriginalImage && originalImage && (
              <div className="image-comparison">
                <div className="comparison-item">
                  <h4>Original Image</h4>
                  <img
                    src={originalImage}
                    alt="Original"
                    className="comparison-image original"
                  />
                </div>
                <div className="comparison-item">
                  <h4>Density Heatmap</h4>
                  <img
                    src={heatmapImage}
                    alt="Density Heatmap"
                    className="comparison-image heatmap"
                  />
                </div>
              </div>
            )}

            {!showOriginalImage && (
              <div className="heatmap-single">
                <img
                  src={heatmapImage}
                  alt="Density Heatmap"
                  className="heatmap-image"
                />
                <div className="heatmap-legend">
                  <div className="legend-item">
                    <span
                      className="legend-color"
                      style={{ background: "#0000ff" }}
                    ></span>
                    <span>Low Density</span>
                  </div>
                  <div className="legend-item">
                    <span
                      className="legend-color"
                      style={{ background: "#00ff00" }}
                    ></span>
                    <span>Medium Density</span>
                  </div>
                  <div className="legend-item">
                    <span
                      className="legend-color"
                      style={{ background: "#ff0000" }}
                    ></span>
                    <span>High Density</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {inferenceTime !== undefined && inferenceTime !== null && !isLoading && (
        <div className="heatmap-card-footer">
          <span className="inference-time">
            ⚡ Inference: {inferenceTime.toFixed(2)}ms
          </span>
        </div>
      )}
    </div>
  );
}
