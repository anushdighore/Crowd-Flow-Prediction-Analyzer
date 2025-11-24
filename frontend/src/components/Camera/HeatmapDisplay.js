import React from "react";
import HeatmapOverlay from "../Heatmap/HeatmapOverlay";

/**
 * HeatmapDisplay Component
 * Shows the heatmap/detection overlay for the camera stream
 */
function HeatmapDisplay({
  heatmapImage,
  enableHeatmap,
  selectedModel,
  heatmapRef,
}) {
  return (
    <HeatmapOverlay
      heatmapImage={heatmapImage}
      enableHeatmap={enableHeatmap}
      modelType={selectedModel}
      displayMode="side-by-side"
      heatmapRef={heatmapRef}
    />
  );
}

export default HeatmapDisplay;
