import React from "react";
import HeatmapOverlay from "../Heatmap/HeatmapOverlay";
import "./VisualizationCards.css";

/**
 * HeatmapCard - Reusable heatmap visualization card
 * Works for: All detection modes (Webcam, External Camera, Video, Image)
 *
 * Props:
 * - isStreaming: boolean
 * - enableHeatmap: boolean
 * - heatmapImage: base64 image string
 * - modelType: string (model name)
 * - displayMode: "card" | "standalone"
 */
function HeatmapCard({
  isStreaming,
  enableHeatmap,
  heatmapImage,
  modelType,
  displayMode = "card",
}) {
  return (
    <div className="viz-card heatmap-card">
      <div className="card-header">
        <h3>🗺️ Detection Heatmap</h3>
      </div>
      <div className="card-content">
        {isStreaming && enableHeatmap && heatmapImage ? (
          <HeatmapOverlay
            heatmapImage={heatmapImage}
            enableHeatmap={enableHeatmap}
            modelType={modelType}
            displayMode="standalone"
          />
        ) : (
          <div className="card-placeholder">
            <div className="placeholder-icon">🗺️</div>
            <p>
              {!isStreaming
                ? "Start detection to view heatmap"
                : "Enable Detection Overlay in settings"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default HeatmapCard;
