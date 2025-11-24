import React from "react";
import "./SettingsSidebar.css";
import { Switch, FormControlLabel } from "@mui/material";

/**
 * SettingsSidebar - Reusable settings panel
 * Works for: All detection modes (Webcam, External Camera, Video, Image)
 *
 * Props:
 * - isStreaming: boolean
 * - error: string | null
 * - selectedModel: string
 * - setSelectedModel: function
 * - autoSwitch: boolean
 * - setAutoSwitch: function
 * - autoSwitchThreshold: number
 * - setAutoSwitchThreshold: function
 * - currentAutoModel: string
 * - detectionThreshold: number
 * - setDetectionThreshold: function
 * - enableTracking: boolean
 * - setEnableTracking: function
 * - enableHeatmap: boolean
 * - setEnableHeatmap: function
 * - showLiveCount: boolean
 * - setShowLiveCount: function
 * - showHeatmap: boolean
 * - setShowHeatmap: function
 * - showGraph: boolean
 * - setShowGraph: function
 * - showMetrics: boolean
 * - setShowMetrics: function
 * - onStart: function
 * - onStop: function
 * - fps: number
 * - frameCount: number
 * - sourceType: "webcam" | "external" | "video" | "image"
 */
function SettingsSidebar({
  isStreaming,
  error,
  selectedModel,
  setSelectedModel,
  autoSwitch,
  setAutoSwitch,
  autoSwitchThreshold,
  setAutoSwitchThreshold,
  currentAutoModel,
  detectionThreshold,
  setDetectionThreshold,
  enableTracking,
  setEnableTracking,
  enableHeatmap,
  setEnableHeatmap,
  showLiveCount,
  setShowLiveCount,
  showHeatmap,
  setShowHeatmap,
  showGraph,
  setShowGraph,
  showMetrics,
  setShowMetrics,
  onStart,
  onStop,
  fps = 0,
  frameCount = 0,
  sourceType = "webcam",
  children,
}) {
  const isYoloModel =
    selectedModel.startsWith("yolo") ||
    (autoSwitch && currentAutoModel.startsWith("yolo"));

  return (
    <aside className="settings-sidebar">
      <h3>⚙️ Settings</h3>

      {error && <div className="error-banner">{error}</div>}

      {/* External Camera IP Settings - Shows only for external camera source */}
      {sourceType === "external" && children && (
        <>
          <div className="setting-group camera-settings">
            <h4>📡 Camera Settings</h4>
            {children}
          </div>
          <hr className="settings-divider" />
        </>
      )}

      {/* Model Selection */}
      <div className="setting-group">
        <label htmlFor="model-select">Model</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={isStreaming || autoSwitch}
        >
          <optgroup label="YOLO (Object Detection)">
            <option value="yolo">YOLO v8 (Default)</option>
            <option value="yolo-nano">🚀 YOLOv8 Nano (Fastest)</option>
            <option value="yolo-small">⚡ YOLOv8 Small</option>
            <option value="yolo-medium">⚙️ YOLOv8 Medium</option>
            <option value="yolo-large">🎯 YOLOv8 Large</option>
            <option value="yolo-xlarge">🔴 YOLOv8 XLarge (Best)</option>
          </optgroup>
          <optgroup label="Density Estimation">
            <option value="csrnet">CSRNet (Fast)</option>
            <option value="tmtb">TMTB/VMamba (Accurate)</option>
          </optgroup>
        </select>
      </div>

      {/* Auto-Switch Mode - Only for streaming sources */}
      {(sourceType === "webcam" ||
        sourceType === "external" ||
        sourceType === "video") && (
        <div className="setting-group">
          <FormControlLabel
            control={
              <Switch
                checked={autoSwitch}
                onChange={(e) => {
                  setAutoSwitch(e.target.checked);
                  if (e.target.checked && currentAutoModel) {
                    // Auto-switch enabled
                  }
                }}
                disabled={isStreaming}
              />
            }
            label="🔄 Auto-Switch Mode"
          />
          {autoSwitch && (
            <div className="threshold-group">
              <label htmlFor="threshold">Threshold:</label>
              <input
                type="number"
                id="threshold"
                value={autoSwitchThreshold}
                onChange={(e) =>
                  setAutoSwitchThreshold(parseInt(e.target.value) || 30)
                }
                disabled={isStreaming}
                min="1"
                max="100"
              />
              <span className="unit">people</span>
            </div>
          )}
        </div>
      )}

      {/* Detection Threshold */}
      <div className="setting-group">
        <label htmlFor="detection-threshold">
          Confidence: {(detectionThreshold * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          id="detection-threshold"
          min="0.1"
          max="0.9"
          step="0.05"
          value={detectionThreshold}
          onChange={(e) => setDetectionThreshold(parseFloat(e.target.value))}
          disabled={isStreaming}
        />
      </div>

      {/* Feature Toggles */}
      <div className="setting-group">
        <h4>Features</h4>

        <FormControlLabel
          control={
            <Switch
              checked={enableTracking}
              onChange={(e) => setEnableTracking(e.target.checked)}
              disabled={isStreaming || !isYoloModel}
            />
          }
          label={`🎯 Tracking ${!isYoloModel ? "(YOLO only)" : ""}`}
        />

        <FormControlLabel
          control={
            <Switch
              checked={enableHeatmap}
              onChange={(e) => setEnableHeatmap(e.target.checked)}
              disabled={isStreaming}
            />
          }
          label="🔥 Detection Overlay"
        />
      </div>

      {/* Display Options */}
      <div className="setting-group">
        <h4>Display</h4>

        <FormControlLabel
          control={
            <Switch
              checked={showLiveCount}
              onChange={(e) => setShowLiveCount(e.target.checked)}
            />
          }
          label="📹 Live Feed"
        />

        <FormControlLabel
          control={
            <Switch
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
            />
          }
          label="🗺️ Heatmap View"
        />

        {(sourceType === "webcam" ||
          sourceType === "external" ||
          sourceType === "video") && (
          <FormControlLabel
            control={
              <Switch
                checked={showGraph}
                onChange={(e) => setShowGraph(e.target.checked)}
              />
            }
            label="📊 Count Graph"
          />
        )}

        <FormControlLabel
          control={
            <Switch
              checked={showMetrics}
              onChange={(e) => setShowMetrics(e.target.checked)}
            />
          }
          label="📈 Metrics"
        />
      </div>

      {/* Controls */}
      <div className="setting-group controls">
        {!isStreaming ? (
          <button onClick={onStart} className="btn btn-start">
            🎬 Start{" "}
            {sourceType === "webcam"
              ? "Streaming"
              : sourceType === "external"
              ? "Camera"
              : "Analysis"}
          </button>
        ) : (
          <button onClick={onStop} className="btn btn-stop">
            ⏹️ Stop{" "}
            {sourceType === "webcam"
              ? "Streaming"
              : sourceType === "external"
              ? "Camera"
              : "Analysis"}
          </button>
        )}
      </div>

      {/* Status Info */}
      {isStreaming && (
        <div className="status-info">
          {fps > 0 && (
            <div className="status-item">
              <span>FPS:</span>
              <span className="status-value">{fps.toFixed(1)}</span>
            </div>
          )}
          {frameCount > 0 && (
            <div className="status-item">
              <span>Frames:</span>
              <span className="status-value">{frameCount}</span>
            </div>
          )}
          <div className="status-item">
            <span>Model:</span>
            <span className="status-value">
              {autoSwitch ? currentAutoModel : selectedModel}
            </span>
          </div>
        </div>
      )}
    </aside>
  );
}

export default SettingsSidebar;
