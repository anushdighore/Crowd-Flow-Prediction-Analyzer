import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/WebcamPage.css";
import { useAuth } from "../context/AuthContext";
import { useWebcam } from "../context/WebcamContext";
import { useExternalCamera } from "../context/ExternalCameraContext";

/**
 * Template Page - Unified camera detection page supporting both webcam and external camera
 * Uses global contexts for state management to integrate with RightMenu
 * Note: This component should NOT include its own Layout - App.js wraps it in Layout
 */
function Template() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Camera Source Mode
  const [cameraMode, setCameraMode] = useState("webcam"); // "webcam" or "external"

  // Get contexts
  const webcamContext = useWebcam();
  const externalCameraContext = useExternalCamera();

  // Destructure from webcam context (for webcam mode)
  const {
    isStreaming: webcamIsStreaming,
    selectedModel: webcamSelectedModel,
    enableTracking: webcamEnableTracking,
    enableHeatmap: webcamEnableHeatmap,
    detectionThreshold: webcamDetectionThreshold,
    fps: webcamFps,
    inferenceTime: webcamInferenceTime,
    error: webcamError,
    results: webcamResults,
    heatmapImage: webcamHeatmap,
    videoRef,
    canvasRef,
    handleStartStreaming: webcamStart,
    handleStopStreaming: webcamStop,
    setSelectedModel: webcamSetSelectedModel,
    setEnableTracking: webcamSetEnableTracking,
    setEnableHeatmap: webcamSetEnableHeatmap,
    setDetectionThreshold: webcamSetDetectionThreshold,
    settings: webcamSettings,
    setSettings: webcamSetSettings,
  } = webcamContext;

  // Destructure from external camera context (for external mode)
  const {
    isStreaming: externalIsStreaming,
    loading: externalLoading,
    cameraUrl,
    demoMode,
    selectedModel: externalSelectedModel,
    enableTracking: externalEnableTracking,
    enableHeatmap: externalEnableHeatmap,
    detectionThreshold: externalDetectionThreshold,
    status: externalStatus,
    count: externalCount,
    fps: externalFps,
    inferenceTime: externalInferenceTime,
    error: externalError,
    autoSwitch,
    autoSwitchThreshold,
    currentAutoModel,
    heatmapImage: externalHeatmap,
    annotatedFrame,
    countHistory,
    fpsHistory,
    notification,
    DEMO_URLS,
    imgRef: externalImgRef,
    heatmapRef: externalHeatmapRef,
    setCameraUrl,
    setDemoMode,
    setAutoSwitch,
    setAutoSwitchThreshold,
    handleStartStreaming: externalStart,
    handleStopStreaming: externalStop,
    testConnection,
    setSelectedModel: externalSetSelectedModel,
    setEnableTracking: externalSetEnableTracking,
    setEnableHeatmap: externalSetEnableHeatmap,
    setDetectionThreshold: externalSetDetectionThreshold,
    settings: externalSettings,
    setSettings: externalSetSettings,
  } = externalCameraContext;

  // Computed values based on mode
  const isStreaming =
    cameraMode === "external" ? externalIsStreaming : webcamIsStreaming;
  const selectedModel =
    cameraMode === "external" ? externalSelectedModel : webcamSelectedModel;
  const enableTracking =
    cameraMode === "external" ? externalEnableTracking : webcamEnableTracking;
  const enableHeatmap =
    cameraMode === "external" ? externalEnableHeatmap : webcamEnableHeatmap;
  const detectionThreshold =
    cameraMode === "external"
      ? externalDetectionThreshold
      : webcamDetectionThreshold;
  const fps = cameraMode === "external" ? externalFps : webcamFps;
  const inferenceTime =
    cameraMode === "external" ? externalInferenceTime : webcamInferenceTime;
  const error = cameraMode === "external" ? externalError : webcamError;
  const heatmap = cameraMode === "external" ? externalHeatmap : webcamHeatmap;
  const count =
    cameraMode === "external" ? externalCount : webcamResults?.count || 0;

  const selectedIsYolo = (selectedModel || "").toLowerCase().includes("yolo");

  const activeSetSelectedModel =
    cameraMode === "external"
      ? externalSetSelectedModel
      : webcamSetSelectedModel;
  const activeSetEnableTracking =
    cameraMode === "external"
      ? externalSetEnableTracking
      : webcamSetEnableTracking;
  const activeSetEnableHeatmap =
    cameraMode === "external"
      ? externalSetEnableHeatmap
      : webcamSetEnableHeatmap;
  const activeSetDetectionThreshold =
    cameraMode === "external"
      ? externalSetDetectionThreshold
      : webcamSetDetectionThreshold;
  const activeSettings =
    cameraMode === "external" ? externalSettings : webcamSettings;
  const activeSetSettings =
    cameraMode === "external" ? externalSetSettings : webcamSetSettings;

  // Handle streaming toggle based on mode
  const handleStartStreaming = useCallback(() => {
    if (cameraMode === "external") {
      externalStart();
    } else {
      webcamStart();
    }
  }, [cameraMode, externalStart, webcamStart]);

  const handleStopStreaming = useCallback(() => {
    if (cameraMode === "external") {
      externalStop();
    } else {
      webcamStop();
    }
  }, [cameraMode, externalStop, webcamStop]);

  // Stop streaming when switching modes
  const handleModeChange = useCallback(
    (newMode) => {
      if (isStreaming) {
        handleStopStreaming();
      }
      setCameraMode(newMode);
    },
    [isStreaming, handleStopStreaming]
  );

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access the template page</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <header
        style={{
          padding: "2rem",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          textAlign: "center",
          marginBottom: "2rem",
        }}
      >
        <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
          📹 Live Detection Template
        </h1>
        <p style={{ fontSize: "1rem", opacity: 0.9 }}>
          Real-time crowd detection with webcam and external camera support
        </p>
      </header>

      {/* Main Content */}
      <div style={{ padding: "0 2rem" }}>
        {/* Notification */}
        {notification && (
          <div
            style={{
              padding: "1rem",
              background:
                notification.type === "success"
                  ? "#d1fae5"
                  : notification.type === "warning"
                  ? "#fef3c7"
                  : "#dbeafe",
              border: `1px solid ${
                notification.type === "success"
                  ? "#6ee7b7"
                  : notification.type === "warning"
                  ? "#fcd34d"
                  : "#93c5fd"
              }`,
              borderRadius: "8px",
              marginBottom: "1.5rem",
              color:
                notification.type === "success"
                  ? "#065f46"
                  : notification.type === "warning"
                  ? "#92400e"
                  : "#1e40af",
            }}
          >
            {notification.message}
          </div>
        )}

        <div
          style={{
            background: "white",
            borderRadius: "12px",
            padding: "1.5rem",
            marginBottom: "2rem",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
          }}
        >
          <h3 style={{ margin: "0 0 1rem 0", color: "#333" }}>
            🎯 Model & Settings
          </h3>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            {[
              { id: "CSRNet", label: "CSRNet" },
              { id: "VMamba", label: "VMamba TMTB" },
              { id: "YOLOv8", label: "YOLOv8" },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => activeSetSelectedModel(m.id)}
                style={{
                  flex: 1,
                  padding: "0.75rem",
                  background:
                    selectedModel === m.id
                      ? "linear-gradient(135deg, #f5f1e8 0%, #f5f1e8 100%)"
                      : "#f3f4f6",
                  color: selectedModel === m.id ? "#333" : "#333",
                  border:
                    selectedModel === m.id
                      ? "2px solid #e5e7eb"
                      : "1px solid #e5e7eb",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: selectedModel === m.id ? "700" : "600",
                }}
              >
                {m.label}
              </button>
            ))}
          </div>

          {selectedModel === "YOLOv8" && (
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="yolo-version"
                style={{ display: "block", marginBottom: "0.5rem" }}
              >
                YOLO Version
              </label>
              <select
                id="yolo-version"
                value={activeSettings?.yoloVersion || "nano"}
                onChange={(e) =>
                  activeSetSettings({
                    ...(activeSettings || {}),
                    yoloVersion: e.target.value,
                  })
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #d1d5db",
                  cursor: "pointer",
                }}
              >
                <option value="nano">Nano</option>
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
                <option value="xlarge">XLarge</option>
              </select>
            </div>
          )}

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "1rem",
            }}
          >
            <label
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              <input
                type="checkbox"
                checked={enableTracking || false}
                onChange={(e) => activeSetEnableTracking(e.target.checked)}
              />
              Tracking
            </label>
            <label
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              <input
                type="checkbox"
                checked={enableHeatmap || false}
                onChange={(e) => activeSetEnableHeatmap(e.target.checked)}
              />
              Heatmap
            </label>
          </div>

          <div style={{ marginTop: "1rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              Confidence: {(Number(detectionThreshold || 0.5) * 100).toFixed(0)}
              %
            </label>
            <input
              type="range"
              min="0.1"
              max="0.95"
              step="0.05"
              value={detectionThreshold || 0.5}
              onChange={(e) =>
                activeSetDetectionThreshold(parseFloat(e.target.value))
              }
              style={{ width: "100%" }}
            />
          </div>
        </div>
        {/* Camera Mode Selector */}
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            padding: "1.5rem",
            marginBottom: "2rem",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
          }}
        >
          <h3 style={{ margin: "0 0 1rem 0", color: "#333" }}>
            📷 Camera Source
          </h3>
          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={() => handleModeChange("webcam")}
              style={{
                flex: 1,
                padding: "1rem",
                background:
                  cameraMode === "webcam"
                    ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                    : "#f3f4f6",
                color: cameraMode === "webcam" ? "white" : "#333",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "600",
                fontSize: "1rem",
                transition: "all 0.3s ease",
              }}
            >
              📹 Webcam
            </button>
            <button
              onClick={() => handleModeChange("external")}
              style={{
                flex: 1,
                padding: "1rem",
                background:
                  cameraMode === "external"
                    ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                    : "#f3f4f6",
                color: cameraMode === "external" ? "white" : "#333",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "600",
                fontSize: "1rem",
                transition: "all 0.3s ease",
              }}
            >
              📡 External Camera
            </button>
          </div>
        </div>

        {/* External Camera URL Input (only shown in external mode) */}
        {cameraMode === "external" && (
          <div
            style={{
              background: "white",
              borderRadius: "12px",
              padding: "1.5rem",
              marginBottom: "2rem",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            <h3 style={{ margin: "0 0 1rem 0", color: "#333" }}>
              🔗 Camera URL
            </h3>
            <div
              style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}
            >
              <input
                type="text"
                value={cameraUrl}
                onChange={(e) => setCameraUrl(e.target.value)}
                placeholder="http://192.168.1.100:8080/video"
                style={{
                  flex: 1,
                  padding: "0.75rem",
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  fontSize: "0.95rem",
                  opacity: demoMode ? 0.5 : 1,
                }}
                disabled={externalIsStreaming || demoMode}
              />
              <button
                onClick={testConnection}
                disabled={externalIsStreaming || externalLoading}
                style={{
                  padding: "0.75rem 1.5rem",
                  background: demoMode ? "#10b981" : "#3b82f6",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: externalIsStreaming ? "not-allowed" : "pointer",
                  opacity: externalIsStreaming ? 0.5 : 1,
                  fontWeight: "600",
                }}
              >
                {demoMode ? "✅ Ready" : "🔍 Test"}
              </button>
            </div>

            {/* Demo Mode Toggle */}
            <div
              style={{
                padding: "1rem",
                background: demoMode ? "#dbeafe" : "#f9fafb",
                borderRadius: "8px",
                border: `1px solid ${demoMode ? "#3b82f6" : "#e5e7eb"}`,
                marginBottom: "1rem",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", alignItems: "center" }}>
                  <input
                    type="checkbox"
                    id="demo-mode"
                    checked={demoMode}
                    onChange={(e) => setDemoMode(e.target.checked)}
                    style={{ marginRight: "0.5rem" }}
                    disabled={externalIsStreaming}
                  />
                  <label
                    htmlFor="demo-mode"
                    style={{
                      fontWeight: "600",
                      color: demoMode ? "#1d4ed8" : "#374151",
                    }}
                  >
                    🎬 Demo Mode
                  </label>
                </div>
                {demoMode && (
                  <span
                    style={{
                      fontSize: "0.75rem",
                      color: "#3b82f6",
                      fontWeight: "500",
                    }}
                  >
                    Using local demo video
                  </span>
                )}
              </div>
              <p
                style={{
                  margin: "0.5rem 0 0 1.5rem",
                  fontSize: "0.8rem",
                  color: "#6b7280",
                }}
              >
                {demoMode
                  ? "Stream will use a pre-recorded demo video for testing"
                  : "Enable to test without a real camera connection"}
              </p>
            </div>

            {/* Auto-Switch Settings */}
            <div
              style={{
                padding: "1rem",
                background: "#f9fafb",
                borderRadius: "8px",
                border: "1px solid #e5e7eb",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: "0.75rem",
                }}
              >
                <input
                  type="checkbox"
                  id="auto-switch"
                  checked={autoSwitch}
                  onChange={(e) => setAutoSwitch(e.target.checked)}
                  style={{ marginRight: "0.5rem" }}
                />
                <label
                  htmlFor="auto-switch"
                  style={{ fontWeight: "600", color: "#374151" }}
                >
                  🔄 Auto-Switch Model
                </label>
              </div>
              {autoSwitch && (
                <div style={{ marginLeft: "1.5rem" }}>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.85rem",
                      color: "#6b7280",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Switch to CSRNet when count ≥
                  </label>
                  <input
                    type="number"
                    value={autoSwitchThreshold}
                    onChange={(e) =>
                      setAutoSwitchThreshold(parseInt(e.target.value) || 30)
                    }
                    min="1"
                    max="100"
                    style={{
                      width: "80px",
                      padding: "0.5rem",
                      border: "1px solid #d1d5db",
                      borderRadius: "4px",
                    }}
                  />
                  <span
                    style={{
                      marginLeft: "0.5rem",
                      fontSize: "0.85rem",
                      color: "#6b7280",
                    }}
                  >
                    Current: {currentAutoModel}
                  </span>
                </div>
              )}
            </div>
            <div
              style={{
                marginTop: "0.75rem",
                fontSize: "0.85rem",
                color: "#6b7280",
              }}
            >
              Status: <strong>{externalStatus}</strong>
              {demoMode && (
                <span style={{ marginLeft: "0.5rem", color: "#3b82f6" }}>
                  (Demo Mode)
                </span>
              )}
            </div>
          </div>
        )}

        {/* Debug Info */}
        <div
          style={{
            padding: "1rem",
            background: "#f3f4f6",
            borderRadius: "8px",
            marginBottom: "1.5rem",
            fontSize: "0.85rem",
            fontFamily: "monospace",
          }}
        >
          <div>📊 Status: {isStreaming ? "🟢 STREAMING" : "⚫ STOPPED"}</div>
          <div>
            📷 Mode:{" "}
            {cameraMode === "external" ? "📡 External Camera" : "📹 Webcam"}
          </div>
          <div>🎬 Model: {selectedModel}</div>
          <div>📤 FPS: {fps?.toFixed?.(1) || fps || 0}</div>
          <div>👥 Count: {Math.round(count)}</div>
          <div>
            ⏱️ Inference: {inferenceTime?.toFixed?.(0) || inferenceTime || 0}ms
          </div>
          <div>🎯 Tracking: {enableTracking ? "✅" : "❌"}</div>
          <div>🔥 Heatmap: {enableHeatmap ? "✅" : "❌"}</div>
        </div>

        {/* Error Display */}
        {error && (
          <div
            style={{
              padding: "1rem",
              background: "#fee2e2",
              border: "1px solid #fca5a5",
              borderRadius: "8px",
              color: "#dc2626",
              marginBottom: "1.5rem",
            }}
          >
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {/* Start/Stop Streaming Button */}
        <div style={{ marginBottom: "2rem" }}>
          <button
            onClick={isStreaming ? handleStopStreaming : handleStartStreaming}
            disabled={cameraMode === "external" && externalLoading}
            style={{
              width: "100%",
              padding: "1rem",
              background: isStreaming
                ? "linear-gradient(135deg, #f87171 0%, #dc2626 100%)"
                : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor:
                cameraMode === "external" && externalLoading
                  ? "not-allowed"
                  : "pointer",
              fontSize: "1.1rem",
              fontWeight: "700",
              transition: "all 0.3s ease",
              boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            }}
          >
            {externalLoading
              ? "⏳ Connecting..."
              : isStreaming
              ? "⏹️ Stop Streaming"
              : "🎬 Start Streaming"}
          </button>
        </div>

        {/* Live Feed Card */}
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            padding: "1.5rem",
            marginBottom: "2rem",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
          }}
        >
          <h2 style={{ margin: "0 0 1rem 0", color: "#333" }}>
            {cameraMode === "external"
              ? "📡 External Camera Feed"
              : "📹 Live Webcam Feed"}
          </h2>
          <div
            style={{
              position: "relative",
              width: "100%",
              paddingBottom: "56.25%",
              background: "#000",
              borderRadius: "8px",
              overflow: "hidden",
            }}
          >
            {cameraMode === "webcam" ? (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                />
                <canvas ref={canvasRef} style={{ display: "none" }} />
              </>
            ) : (
              <img
                ref={externalImgRef}
                alt="External Camera Feed"
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  display: externalIsStreaming ? "block" : "none",
                }}
              />
            )}

            {/* Annotated Frame Overlay (for external camera with tracking) */}
            {cameraMode === "external" &&
              annotatedFrame &&
              externalIsStreaming && (
                <img
                  src={annotatedFrame}
                  alt="Annotated Frame with Trajectories"
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    zIndex: 1,
                  }}
                />
              )}

            {!isStreaming && (
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "white",
                  fontSize: "1.2rem",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                <span>
                  {cameraMode === "external"
                    ? "Configure camera URL and click Start Streaming"
                    : "Click Start Streaming to begin"}
                </span>
              </div>
            )}
          </div>

          {/* Stats */}
          {isStreaming && (
            <div
              style={{
                marginTop: "1rem",
                fontSize: "0.9rem",
                color: "#666",
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "0.5rem",
              }}
            >
              <div
                style={{
                  padding: "0.5rem",
                  background: "#f9fafb",
                  borderRadius: "4px",
                }}
              >
                👥 Count: <strong>{Math.round(count)}</strong>
              </div>
              <div
                style={{
                  padding: "0.5rem",
                  background: "#f9fafb",
                  borderRadius: "4px",
                }}
              >
                📤 FPS: <strong>{fps?.toFixed?.(1) || fps || 0}</strong>
              </div>
              <div
                style={{
                  padding: "0.5rem",
                  background: "#f9fafb",
                  borderRadius: "4px",
                }}
              >
                ⏱️ Inference:{" "}
                <strong>
                  {inferenceTime?.toFixed?.(0) || inferenceTime || 0}ms
                </strong>
              </div>
              <div
                style={{
                  padding: "0.5rem",
                  background: "#f9fafb",
                  borderRadius: "4px",
                }}
              >
                🎬 Model: <strong>{selectedModel}</strong>
              </div>
            </div>
          )}
        </div>

        {/* Heatmap Card */}
        {enableHeatmap && heatmap && isStreaming && !selectedIsYolo && (
          <div
            style={{
              background: "white",
              borderRadius: "12px",
              padding: "1.5rem",
              marginBottom: "2rem",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            <h2 style={{ margin: "0 0 1rem 0", color: "#333" }}>
              🔥 Heatmap Visualization
            </h2>
            <div
              style={{
                position: "relative",
                width: "100%",
                paddingBottom: "56.25%",
                background: "#000",
                borderRadius: "8px",
                overflow: "hidden",
              }}
            >
              <img
                ref={cameraMode === "external" ? externalHeatmapRef : undefined}
                src={
                  heatmap.startsWith("data:")
                    ? heatmap
                    : `data:image/png;base64,${heatmap}`
                }
                alt="Heatmap"
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }}
              />
            </div>
          </div>
        )}

        {/* Analytics Charts (for external camera) */}
        {cameraMode === "external" &&
          isStreaming &&
          (countHistory.length > 0 || fpsHistory.length > 0) && (
            <div
              style={{
                background: "white",
                borderRadius: "12px",
                padding: "1.5rem",
                marginBottom: "2rem",
                boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
              }}
            >
              <h2 style={{ margin: "0 0 1rem 0", color: "#333" }}>
                📊 Real-time Analytics
              </h2>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1rem",
                }}
              >
                <div
                  style={{
                    padding: "1rem",
                    background: "#f9fafb",
                    borderRadius: "8px",
                  }}
                >
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#374151" }}>
                    Count History
                  </h4>
                  <div
                    style={{
                      height: "100px",
                      display: "flex",
                      alignItems: "flex-end",
                      gap: "2px",
                    }}
                  >
                    {countHistory.slice(-20).map((item, i) => (
                      <div
                        key={i}
                        style={{
                          flex: 1,
                          height: `${Math.min(
                            100,
                            (item.count /
                              Math.max(
                                ...countHistory.map((h) => h.count),
                                1
                              )) *
                              100
                          )}%`,
                          background:
                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          borderRadius: "2px 2px 0 0",
                          minHeight: "4px",
                        }}
                        title={`Count: ${Math.round(item.count)}`}
                      />
                    ))}
                  </div>
                </div>
                <div
                  style={{
                    padding: "1rem",
                    background: "#f9fafb",
                    borderRadius: "8px",
                  }}
                >
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#374151" }}>
                    FPS History
                  </h4>
                  <div
                    style={{
                      height: "100px",
                      display: "flex",
                      alignItems: "flex-end",
                      gap: "2px",
                    }}
                  >
                    {fpsHistory.slice(-20).map((item, i) => (
                      <div
                        key={i}
                        style={{
                          flex: 1,
                          height: `${Math.min(
                            100,
                            (item.fps /
                              Math.max(...fpsHistory.map((h) => h.fps), 1)) *
                              100
                          )}%`,
                          background:
                            "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                          borderRadius: "2px 2px 0 0",
                          minHeight: "4px",
                        }}
                        title={`FPS: ${item.fps?.toFixed(1)}`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
      </div>
    </>
  );
}

export default Template;
