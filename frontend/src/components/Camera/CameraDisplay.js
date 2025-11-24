import React from "react";
import TrajectoryCanvas from "../Trajectory/TrajectoryCanvas";

/**
 * CameraDisplay Component
 * Shows the live camera feed with trajectory overlay and count display
 */
function CameraDisplay({
  imgRef,
  results,
  enableTracking,
  autoSwitch,
  currentAutoModel,
}) {
  return (
    <div className="video-frame">
      <div className="frame-label">📹 Camera Feed</div>
      <div className="video-container" style={{ position: "relative" }}>
        <img
          ref={imgRef}
          alt="External camera stream"
          className="video-feed"
          style={{ width: "100%", height: "auto", display: "block" }}
        />

        {/* Trajectory overlay */}
        <TrajectoryCanvas
          sourceRef={imgRef}
          results={results}
          enableTracking={enableTracking}
        />

        {/* Count and model badge overlay */}
        {results && (
          <div className="overlay">
            <div className="count-display">
              👥 Count:{" "}
              <span className="count-number">{Math.round(results.count)}</span>
            </div>
            {autoSwitch && (
              <div className="auto-model-badge">
                🔄 {currentAutoModel.toUpperCase()}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CameraDisplay;
