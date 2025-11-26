import React, { useState } from "react";
import { Switch, FormControlLabel } from "@mui/material";
import { useExternalCamera } from "../../context/ExternalCameraContext";

function MainRightMenu({ isOpen = true, onToggle }) {
  const [localOpen, setLocalOpen] = useState(isOpen);

  // Get external camera context
  const {
    isStreaming,
    selectedModel,
    enableTracking,
    enableHeatmap,
    detectionThreshold,
    settings,
    status,
    count,
    fps,
    inferenceTime,
    frameCount,
    error,
    results,
    heatmapImage,
    annotatedFrame,
    notification,
    densityModelActive,
    yoloActive,
    trackingActive,
    trajectoryTracks,
    showAnnotatedFrame,
    imgRef,
    wsRef,
    setCameraUrl,
    setSelectedModel,
    setEnableTracking,
    setEnableHeatmap,
    setDetectionThreshold,
    setSettings,
    handleStartStreaming,
    handleStopStreaming,
    testConnection,
    stopEverything,
    sendOccupancyConfig,
  } = useExternalCamera();

  const handleToggle = () => {
    setLocalOpen(!localOpen);
    if (onToggle) onToggle(!localOpen);
  };

  const handleModelSelect = (modelId) => {
    console.log(" Model selected:", modelId);
    setSelectedModel(modelId);
  };

  const handleSettingChange = (key, value) => {
    setSettings({ ...settings, [key]: value });
  };

  const handleStreamToggle = () => {
    if (isStreaming) {
      handleStopStreaming();
    } else {
      handleStartStreaming();
    }
  };

  // Occupancy settings state - load from localStorage on init
  const [occupancySettings, setOccupancySettings] = useState(() => {
    const saved = localStorage.getItem("occupancySettings");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          maxCapacity: parsed.max_capacity || 100,
          alertThreshold: parsed.alert_threshold || 80,
          resetThreshold: parsed.reset_threshold || 78,
          windowSize: parsed.window_size || 3,
        };
      } catch (e) {
        console.error("Error parsing saved occupancy settings:", e);
      }
    }
    return {
      maxCapacity: 100,
      alertThreshold: 80,
      resetThreshold: 78,
      windowSize: 3,
    };
  });

  const handleOccupancySettingChange = (key, value) => {
    const newSettings = { ...occupancySettings, [key]: value };
    setOccupancySettings(newSettings);

    // Prepare config object for backend
    const configForBackend = {
      max_capacity: newSettings.maxCapacity,
      alert_threshold: newSettings.alertThreshold,
      reset_threshold: newSettings.resetThreshold,
      window_size: newSettings.windowSize,
    };

    // Save to localStorage for persistence
    localStorage.setItem("occupancySettings", JSON.stringify(configForBackend));

    // Send updated configuration to backend via WebSocket
    sendOccupancyConfig(configForBackend);
  };

  // Model options with descriptions
  const modelOptions = [
    { id: "CSRNet", desc: " CSRNet (Density Map)", icon: "" },
    { id: "VMamba", desc: " VMamba (Best Accuracy)", icon: "" },
    { id: "YOLOv8", desc: " YOLOv8 (Real-time)", icon: "" },
  ];

  return (
    <aside
      className="right-menu"
      style={{
        width: localOpen ? "320px" : "50px",
        background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        color: "white",
        height: "calc(100vh - 65px)",
        padding: localOpen ? "1.5rem" : "0.75rem",
        borderLeft: "1px solid rgba(255,255,255,0.1)",
        overflowY: "auto",
        transition: "all 0.3s ease",
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        position: "fixed",
        right: 0,
        top: "65px",
        zIndex: 1000,
      }}
    >
      {/* Sidebar Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
          paddingBottom: "1rem",
          borderBottom: "1px solid rgba(255,255,255,0.2)",
        }}
      >
        {localOpen && (
          <h3 style={{ margin: 0, fontSize: "1.1rem" }}>⚙️ Settings</h3>
        )}
        <button
          onClick={handleToggle}
          style={{
            background: "rgba(255,255,255,0.2)",
            color: "white",
            border: "none",
            width: "32px",
            height: "32px",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "1.2rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 101,
            transition: "all 0.3s ease",
            flexShrink: 0,
            marginLeft: localOpen ? "auto" : "0",
          }}
          onMouseEnter={(e) => {
            e.target.style.background = "rgba(255,255,255,0.3)";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "rgba(255,255,255,0.2)";
          }}
          title={localOpen ? "Close sidebar" : "Open sidebar"}
        >
          {localOpen ? "✕" : "☰"}
        </button>
      </div>

      {/* Sidebar Content */}
      {localOpen && (
        <>
          {/* Start/Stop Stream Button */}
          <button
            onClick={handleStreamToggle}
            style={{
              width: "100%",
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              background: isStreaming
                ? "linear-gradient(135deg, #f87171 0%, #dc2626 100%)"
                : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              border: "2px solid rgba(255,255,255,0.3)",
              color: "white",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.95rem",
              fontWeight: "600",
              transition: "all 0.3s ease",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
            onMouseEnter={(e) => {
              e.target.style.border = "2px solid rgba(255,255,255,0.6)";
              e.target.style.transform = "translateY(-2px)";
              e.target.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
            }}
            onMouseLeave={(e) => {
              e.target.style.border = "2px solid rgba(255,255,255,0.3)";
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "none";
            }}
          >
            {isStreaming ? "⏹️ Stop Stream" : "📡 Start Stream"}
          </button>

          {/* Model Selection */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              🤖 Model Selection
            </h4>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
              }}
            >
              {modelOptions.map((model) => (
                <button
                  key={model.id}
                  onClick={() => handleModelSelect(model.id)}
                  style={{
                    padding: "0.75rem 0.75rem",
                    textAlign: "left",
                    display: "flex",
                    flexDirection: "column",
                    background:
                      selectedModel === model.id
                        ? "rgba(255,255,255,0.3)"
                        : "rgba(255,255,255,0.1)",
                    border:
                      selectedModel === model.id
                        ? "1px solid rgba(255,255,255,0.5)"
                        : "1px solid rgba(255,255,255,0.2)",
                    color: "white",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(255,255,255,0.4)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background =
                      selectedModel === model.id
                        ? "rgba(255,255,255,0.3)"
                        : "rgba(255,255,255,0.1)";
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.9rem",
                      fontWeight: "600",
                      marginBottom: "0.25rem",
                      opacity: selectedModel === model.id ? 0.7 : 0.8,
                    }}
                  >
                    {model.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Occupancy Settings */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              📊 Occupancy Settings
            </h4>

            {/* Max Capacity Input */}
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="max-capacity"
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                }}
              >
                Max Capacity
              </label>
              <input
                id="max-capacity"
                type="number"
                placeholder="100"
                min="1"
                max="10000"
                value={occupancySettings.maxCapacity}
                onChange={(e) =>
                  handleOccupancySettingChange(
                    "maxCapacity",
                    parseInt(e.target.value) || 100
                  )
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "none",
                  fontSize: "0.85rem",
                  backgroundColor: "rgba(0,0,0,0.2)",
                  color: "white",
                }}
              />
            </div>

            {/* Alert Threshold Slider */}
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="alert-threshold"
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                }}
              >
                Alert Threshold: {occupancySettings.alertThreshold}%
              </label>
              <input
                id="alert-threshold"
                type="range"
                min="50"
                max="100"
                value={occupancySettings.alertThreshold}
                onChange={(e) =>
                  handleOccupancySettingChange(
                    "alertThreshold",
                    parseInt(e.target.value)
                  )
                }
                style={{
                  width: "100%",
                  height: "6px",
                  borderRadius: "3px",
                  backgroundColor: "rgba(255,255,255,0.3)",
                  outline: "none",
                }}
              />
            </div>

            {/* Reset Threshold Slider */}
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="reset-threshold"
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                }}
              >
                Reset Threshold: {occupancySettings.resetThreshold}%
              </label>
              <input
                id="reset-threshold"
                type="range"
                min="40"
                max="95"
                value={occupancySettings.resetThreshold}
                onChange={(e) =>
                  handleOccupancySettingChange(
                    "resetThreshold",
                    parseInt(e.target.value)
                  )
                }
                style={{
                  width: "100%",
                  height: "6px",
                  borderRadius: "3px",
                  backgroundColor: "rgba(255,255,255,0.3)",
                  outline: "none",
                }}
              />
            </div>

            {/* Window Size Selector */}
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="window-size"
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                }}
              >
                Sliding Window
              </label>
              <select
                id="window-size"
                value={occupancySettings.windowSize}
                onChange={(e) =>
                  handleOccupancySettingChange(
                    "windowSize",
                    parseInt(e.target.value)
                  )
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "none",
                  fontSize: "0.85rem",
                  cursor: "pointer",
                  backgroundColor: "rgba(0,0,0,0.2)",
                  color: "white",
                }}
              >
                <option value="3">3 seconds</option>
                <option value="4">4 seconds</option>
                <option value="5">5 seconds</option>
              </select>
            </div>
          </div>

          {/* YOLO Settings - Conditional submenu */}
          {selectedModel === "YOLOv8" && (
            <div
              style={{
                marginBottom: "1.5rem",
                padding: "1rem",
                background: "rgba(255,255,255,0.1)",
                borderRadius: "6px",
                border: "1px solid rgba(255,255,255,0.2)",
              }}
            >
              <h4
                style={{
                  margin: "0 0 0.75rem",
                  fontSize: "0.95rem",
                  textTransform: "uppercase",
                  opacity: 0.9,
                  letterSpacing: "0.05em",
                }}
              >
                ⚙️ YOLO Settings
              </h4>

              {/* YOLO Version Selection */}
              <div style={{ marginBottom: "1rem" }}>
                <label
                  htmlFor="yolo-version"
                  style={{
                    display: "block",
                    marginBottom: "0.5rem",
                    fontSize: "0.9rem",
                    fontWeight: "600",
                  }}
                >
                  Model Version
                </label>
                <select
                  id="yolo-version"
                  value={settings.yoloVersion || "nano"}
                  onChange={(e) =>
                    handleSettingChange("yoloVersion", e.target.value)
                  }
                  style={{
                    width: "100%",
                    padding: "0.5rem",
                    borderRadius: "4px",
                    border: "none",
                    fontSize: "0.85rem",
                    cursor: "pointer",
                    backgroundColor: "rgba(0,0,0,0.2)",
                    color: "white",
                  }}
                >
                  <option value="nano">🚀 Nano (Fastest)</option>
                  <option value="small">⚡ Small</option>
                  <option value="medium">⚙️ Medium</option>
                  <option value="large">🎯 Large</option>
                  <option value="xlarge">🔴 XLarge (Best)</option>
                </select>
              </div>

              {/* YOLO Feature Toggles */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                }}
              >
                <FormControlLabel
                  control={
                    <Switch
                      checked={enableTracking || false}
                      onChange={(e) => setEnableTracking(e.target.checked)}
                      size="small"
                      sx={{
                        color: "rgba(255,255,255,0.5)",
                        "&.Mui-checked": {
                          color: "rgba(255,255,255,0.9)",
                        },
                      }}
                    />
                  }
                  label="🎯 Enable Tracking"
                  sx={{
                    color: "white",
                    fontSize: "0.9rem",
                    margin: 0,
                  }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={enableHeatmap || false}
                      onChange={(e) => setEnableHeatmap(e.target.checked)}
                      size="small"
                      sx={{
                        color: "rgba(255,255,255,0.5)",
                        "&.Mui-checked": {
                          color: "rgba(255,255,255,0.9)",
                        },
                      }}
                    />
                  }
                  label="🔥 Show Heatmap"
                  sx={{
                    color: "white",
                    fontSize: "0.9rem",
                    margin: 0,
                  }}
                />
              </div>

              {/* Confidence Threshold */}
              <div style={{ marginTop: "1rem" }}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "0.5rem",
                    fontSize: "0.85rem",
                    fontWeight: "600",
                  }}
                >
                  Confidence: {(detectionThreshold * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="0.95"
                  step="0.05"
                  value={detectionThreshold}
                  onChange={(e) =>
                    setDetectionThreshold(parseFloat(e.target.value))
                  }
                  style={{
                    width: "100%",
                    cursor: "pointer",
                    accentColor: "#fff",
                  }}
                />
              </div>
            </div>
          )}

          {/* General Display Settings */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              📺 Display Options
            </h4>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={enableHeatmap || false}
                    onChange={(e) => setEnableHeatmap(e.target.checked)}
                    size="small"
                    sx={{
                      color: "rgba(255,255,255,0.5)",
                      "&.Mui-checked": {
                        color: "rgba(255,255,255,0.9)",
                      },
                    }}
                  />
                }
                label="🔥 Heatmap"
                sx={{
                  color: "white",
                  fontSize: "0.9rem",
                  margin: 0,
                }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.liveFeed || false}
                    onChange={(e) =>
                      handleSettingChange("liveFeed", e.target.checked)
                    }
                    size="small"
                    sx={{
                      color: "rgba(255,255,255,0.5)",
                      "&.Mui-checked": {
                        color: "rgba(255,255,255,0.9)",
                      },
                    }}
                  />
                }
                label="📹 Live Feed"
                sx={{
                  color: "white",
                  fontSize: "0.9rem",
                  margin: 0,
                }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.metrics || false}
                    onChange={(e) =>
                      handleSettingChange("metrics", e.target.checked)
                    }
                    size="small"
                    sx={{
                      color: "rgba(255,255,255,0.5)",
                      "&.Mui-checked": {
                        color: "rgba(255,255,255,0.9)",
                      },
                    }}
                  />
                }
                label="📊 Metrics"
                sx={{
                  color: "white",
                  fontSize: "0.9rem",
                  margin: 0,
                }}
              />
            </div>
          </div>

          {/* Feature Toggles */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              ⚙️ Features
            </h4>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={enableTracking}
                    onChange={(e) => setEnableTracking(e.target.checked)}
                    size="small"
                    sx={{
                      color: "rgba(255,255,255,0.5)",
                      "&.Mui-checked": {
                        color: "rgba(255,255,255,0.9)",
                      },
                    }}
                  />
                }
                label="🎯 Tracking"
                sx={{
                  color: "white",
                  fontSize: "0.9rem",
                  margin: 0,
                }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={enableHeatmap}
                    onChange={(e) => setEnableHeatmap(e.target.checked)}
                    size="small"
                    sx={{
                      color: "rgba(255,255,255,0.5)",
                      "&.Mui-checked": {
                        color: "rgba(255,255,255,0.9)",
                      },
                    }}
                  />
                }
                label="🔥 Heatmap"
                sx={{
                  color: "white",
                  fontSize: "0.9rem",
                  margin: 0,
                }}
              />
            </div>
          </div>

          {/* Resolution Settings */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              🎬 Resolution
            </h4>
            <select
              value={settings.resolution || "high"}
              onChange={(e) =>
                handleSettingChange("resolution", e.target.value)
              }
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "none",
                fontSize: "0.9rem",
                cursor: "pointer",
                backgroundColor: "rgba(0,0,0,0.2)",
                color: "white",
              }}
            >
              <option value="low">Low (Fast)</option>
              <option value="medium">Medium</option>
              <option value="high">High (Quality)</option>
            </select>
          </div>

          {/* Model Info */}
          <div
            style={{
              padding: "1rem",
              background: "rgba(255,255,255,0.1)",
              borderRadius: "6px",
              fontSize: "0.85rem",
              lineHeight: "1.5",
            }}
          >
            <div>{selectedModel}</div>
            <div style={{ opacity: 0.8, marginTop: "0.5rem" }}>
              {selectedModel === "CSRNet" && "Density-map baseline"}
              {selectedModel === "VMamba" && "Fine-tuned best accuracy"}
              {selectedModel === "YOLOv8" &&
                `Real-time (${settings.yoloVersion || "nano"})`}
            </div>
          </div>

          {/* Status Display */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h4
              style={{
                margin: "0 0 0.75rem",
                fontSize: "0.95rem",
                textTransform: "uppercase",
                opacity: 0.9,
                letterSpacing: "0.05em",
              }}
            >
              📊 Status
            </h4>
            <div
              style={{
                padding: "0.75rem",
                backgroundColor: "rgba(255,255,255,0.1)",
                borderRadius: "6px",
                fontSize: "0.85rem",
                lineHeight: "1.4",
              }}
            >
              <div style={{ marginBottom: "0.25rem" }}>
                <strong>Model:</strong> {selectedModel}
              </div>
              <div style={{ marginBottom: "0.25rem" }}>
                <strong>Status:</strong>{" "}
                {isStreaming ? "🟢 Streaming" : "🔴 Stopped"}
              </div>
              {isStreaming && (
                <>
                  <div style={{ marginBottom: "0.25rem" }}>
                    <strong>Count:</strong> {count || 0}
                  </div>
                  <div style={{ marginBottom: "0.25rem" }}>
                    <strong>FPS:</strong> {fps?.toFixed(1) || "0.0"}
                  </div>
                </>
              )}
              {error && (
                <div style={{ color: "#fbbf24", marginTop: "0.5rem" }}>
                  <strong>Error:</strong> {error}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </aside>
  );
}

export default MainRightMenu;
