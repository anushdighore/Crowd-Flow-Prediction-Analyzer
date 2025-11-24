import React from "react";
import "./HeatmapOverlay.css";

/**
 * HeatmapOverlay Component
 *
 * Displays heatmap or detection overlay image from model predictions.
 * Can be displayed as standalone or side-by-side with original feed.
 *
 * @param {Object} props - Component props
 * @param {string} props.heatmapImage - Base64 encoded image data URL
 * @param {boolean} props.enableHeatmap - Whether to display the heatmap
 * @param {string} props.modelType - Current model type (yolo/csrnet/mcnn)
 * @param {string} props.displayMode - 'standalone' or 'side-by-side'
 * @param {string} props.title - Custom title for the overlay (default: "Detection Overlay")
 * @param {React.RefObject} props.heatmapRef - Optional ref for the heatmap image element
 */
export default function HeatmapOverlay({
  heatmapImage,
  enableHeatmap,
  modelType = "yolo",
  displayMode = "standalone",
  title = "Detection Overlay",
  heatmapRef,
}) {
  // Don't render if heatmap is disabled or no image available
  if (!enableHeatmap || !heatmapImage) {
    return null;
  }

  // Determine title based on model type
  const getOverlayTitle = () => {
    if (title !== "Detection Overlay") {
      return title;
    }

    switch (modelType) {
      case "csrnet":
      case "mcnn":
        return " Density Heatmap";
      case "yolo-nano":
      case "yolo-small":
        return " Detection Overlay";
      default:
        return " Detection Overlay";
    }
  };

  // Determine hint text based on model type
  const getHintText = () => {
    switch (modelType) {
      case "csrnet":
      case "mcnn":
        return "💡 Heatmap shows crowd density distribution (brighter = higher density)";
      case "yolo-nano":
      case "yolo-small":
        return "💡 Bounding boxes show detected people with confidence scores";
      default:
        return "💡 Bounding boxes show detected people with confidence scores";
    }
  };

  // Standalone display mode (used in WebcamCounter)
  if (displayMode === "standalone") {
    return (
      <div className="heatmap-wrapper">
        <div className="heatmap-container">
          <img
            ref={heatmapRef}
            src={heatmapImage}
            alt={getOverlayTitle()}
            className="heatmap-image"
          />
        </div>
        <p className="heatmap-hint">{getHintText()}</p>
      </div>
    );
  }

  // Side-by-side display mode (used in ExternalCam)
  if (displayMode === "side-by-side") {
    return (
      <div className="video-frame">
        <div className="frame-label">{getOverlayTitle()}</div>
        <div className="video-container" style={{ position: "relative" }}>
          <img
            ref={heatmapRef}
            src={heatmapImage}
            alt={getOverlayTitle()}
            className="video-feed"
            style={{ width: "100%", height: "auto", display: "block" }}
          />
        </div>
        <p
          className="heatmap-hint"
          style={{
            textAlign: "center",
            fontSize: "0.85rem",
            marginTop: "0.5rem",
          }}
        >
          {getHintText()}
        </p>
      </div>
    );
  }

  return null;
}
