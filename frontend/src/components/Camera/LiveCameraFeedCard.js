/**
 * LiveCameraFeedCard Component - Modular Live Camera Feed Card
 *
 * Reusable component for displaying live camera feed with optional overlays
 * Can be integrated into:
 * - Webcam page
 * - External Camera page
 * - Video upload page
 *
 * Props:
 * - videoRef (ref): Reference to video element
 * - canvasRef (ref): Reference to canvas element
 * - isStreaming (boolean): Whether stream is active
 * - results (object): Detection results to display
 * - enableTracking (boolean): Show trajectory overlay
 * - fps (number): Frames per second
 * - currentModel (string): Current model name
 * - autoSwitch (boolean): Whether auto-switch is enabled
 * - sourceType (string): "webcam" | "external" | "video" | "image"
 * - showMetrics (boolean): Show FPS and other metrics
 */

import React from "react";
import TrajectoryCanvas from "../Trajectory/TrajectoryCanvas";
import CountDisplay from "../CountDisplay";
import "./LiveCameraFeedCard.css";

function LiveCameraFeedCard({
  videoRef,
  canvasRef,
  isStreaming,
  results,
  enableTracking = false,
  fps = 0,
  currentModel = "yolo-nano",
  autoSwitch = false,
  sourceType = "webcam",
  showMetrics = true,
}) {
  return (
    <div className="live-camera-feed-card">
      <div className="feed-card-header">
        <h3 className="feed-card-title">
          {sourceType === "webcam" && "📹 Live Webcam Feed"}
          {sourceType === "external" && "📷 External Camera Feed"}
          {sourceType === "video" && "🎬 Video Feed"}
          {sourceType === "image" && "🖼️ Image Analysis"}
        </h3>
        {isStreaming && (
          <div className="stream-status">
            <span className="status-indicator"></span>
            <span className="status-text">LIVE</span>
          </div>
        )}
      </div>

      <div className="feed-card-content">
        <div className="feed-video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="feed-video"
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />

          {/* Trajectory overlay */}
          {enableTracking && isStreaming && (
            <TrajectoryCanvas
              sourceRef={videoRef}
              results={results}
              enableTracking={enableTracking}
            />
          )}

          {/* Count overlay */}
          {isStreaming && (
            <CountDisplay
              results={results}
              enableTracking={enableTracking}
              displayMode="overlay"
              fps={fps}
              currentModel={currentModel}
              autoSwitch={autoSwitch}
            />
          )}

          {!isStreaming && (
            <div className="feed-placeholder">
              <div className="placeholder-icon">📹</div>
              <p className="placeholder-text">Camera feed will appear here</p>
            </div>
          )}
        </div>

        {/* Metrics Display */}
        {showMetrics && isStreaming && (
          <div className="feed-metrics">
            <div className="metric-item">
              <span className="metric-label">FPS:</span>
              <span className="metric-value">{fps.toFixed(1)}</span>
            </div>
            {results && (
              <div className="metric-item">
                <span className="metric-label">Count:</span>
                <span className="metric-value">{Math.round(results.count || 0)}</span>
              </div>
            )}
            <div className="metric-item">
              <span className="metric-label">Model:</span>
              <span className="metric-value">{currentModel.toUpperCase()}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveCameraFeedCard;
