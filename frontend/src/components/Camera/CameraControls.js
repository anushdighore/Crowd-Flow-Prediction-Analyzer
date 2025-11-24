import React from "react";

/**
 * CameraControls Component
 * Handles camera URL input, model selection, and stream control buttons
 */
function CameraControls({
  cameraUrl,
  onCameraUrlChange,
  selectedModel,
  onModelChange,
  autoSwitch,
  onAutoSwitchChange,
  autoSwitchThreshold,
  onThresholdChange,
  isStreaming,
  loading,
  onTestConnection,
  onStartStream,
  onStopStream,
  error,
  onShowSettings,
  showSettings,
}) {
  return (
    <div className="controls-panel">
      {/* Camera URL Input */}
      <div className="input-group">
        <label>Camera URL:</label>
        <input
          type="text"
          value={cameraUrl}
          onChange={(e) => onCameraUrlChange(e.target.value)}
          placeholder="http://192.168.137.168:8080/video"
          disabled={isStreaming}
          className={isStreaming ? "disabled" : ""}
        />
      </div>

      {/* Model Selection */}
      <div className="input-group">
        <label>Select Model:</label>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={isStreaming || autoSwitch}
          className={isStreaming || autoSwitch ? "disabled" : ""}
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

      {/* Settings Button */}
      <div className="input-group">
        <button
          onClick={() => onShowSettings(!showSettings)}
          className="btn btn-settings"
          disabled={isStreaming}
        >
          ⚙️ {showSettings ? "Hide" : "Show"} Settings
        </button>
      </div>

      {/* Auto-Switch Controls */}
      <div className="auto-switch-toggle">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={autoSwitch}
            onChange={(e) => onAutoSwitchChange(e.target.checked)}
            disabled={isStreaming}
          />
          🔄 Auto-Switch Mode (YOLO ↔ CSRNet)
        </label>
        {autoSwitch && (
          <div className="threshold-input">
            <label htmlFor="threshold-ext">Threshold:</label>
            <input
              type="number"
              id="threshold-ext"
              value={autoSwitchThreshold}
              onChange={(e) =>
                onThresholdChange(parseInt(e.target.value) || 30)
              }
              disabled={isStreaming}
              min="1"
              max="100"
              className="threshold-number"
            />
            <span className="threshold-hint">people</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="button-group">
        <button
          onClick={onTestConnection}
          disabled={loading || isStreaming}
          className="btn btn-test"
        >
          🔍 Test Camera
        </button>
        {!isStreaming ? (
          <button
            onClick={onStartStream}
            disabled={loading}
            className="btn btn-start"
          >
            {loading ? "⏳ Starting..." : "▶️ Start Stream"}
          </button>
        ) : (
          <button onClick={onStopStream} className="btn btn-stop">
            ⏹️ Stop Stream
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && <div className="error-message">⚠️ {error}</div>}
    </div>
  );
}

export default CameraControls;
