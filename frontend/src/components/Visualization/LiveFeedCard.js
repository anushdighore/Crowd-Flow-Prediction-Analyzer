import React from "react";
import TrajectoryCanvas from "../Trajectory/TrajectoryCanvas";
import CountDisplay from "../CountDisplay";
import "./VisualizationCards.css";

/**
 * LiveFeedCard - Reusable live video/webcam feed card
 * Works for: Webcam, External Camera, Video Upload, Image Upload
 *
 * Props:
 * - videoRef: ref to video element
 * - canvasRef: ref to canvas element
 * - isStreaming: boolean
 * - results: detection results object
 * - enableTracking: boolean
 * - fps: number
 * - currentModel: string
 * - autoSwitch: boolean
 * - uniqueCount: number
 * - sourceType: "webcam" | "external" | "video" | "image"
 */
function LiveFeedCard({
  videoRef,
  canvasRef,
  isStreaming,
  results,
  enableTracking,
  fps,
  currentModel,
  autoSwitch,
  uniqueCount,
  sourceType = "webcam",
}) {
  return (
    <div className="viz-card live-count-card">
      <div className="card-header">
        <h3>
          {sourceType === "webcam" && "📹 Live Webcam Feed"}
          {sourceType === "external" && "📷 External Camera Feed"}
          {sourceType === "video" && "🎬 Video Feed"}
          {sourceType === "image" && "🖼️ Image Analysis"}
        </h3>
      </div>
      <div className="card-content">
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="webcam-video"
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />

          {/* Trajectory overlay */}
          {enableTracking && (
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
            <div className="video-placeholder">
              <div className="placeholder-content">
                <div className="camera-icon">
                  {sourceType === "webcam" && "📹"}
                  {sourceType === "external" && "📷"}
                  {sourceType === "video" && "🎬"}
                  {sourceType === "image" && "🖼️"}
                </div>
                <p>
                  {sourceType === "webcam" &&
                    "Click 'Start' to begin webcam streaming"}
                  {sourceType === "external" &&
                    "Connect external camera to start"}
                  {sourceType === "video" && "Upload a video to analyze"}
                  {sourceType === "image" && "Upload an image to analyze"}
                </p>
              </div>
            </div>
          )}
        </div>

        {isStreaming && results && (
          <div className="count-stats">
            <div className="stat-box">
              <span className="stat-label">Count</span>
              <span className="stat-value">{results.count || 0}</span>
            </div>
            {enableTracking && (
              <div className="stat-box">
                <span className="stat-label">Unique</span>
                <span className="stat-value">{uniqueCount || 0}</span>
              </div>
            )}
            <div className="stat-box">
              <span className="stat-label">Confidence</span>
              <span className="stat-value">
                {results.confidence_stats?.avg
                  ? `${(results.confidence_stats.avg * 100).toFixed(0)}%`
                  : "N/A"}
              </span>
            </div>
            {fps > 0 && (
              <div className="stat-box">
                <span className="stat-label">FPS</span>
                <span className="stat-value">{fps.toFixed(1)}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveFeedCard;
