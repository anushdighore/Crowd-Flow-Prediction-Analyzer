import React, { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/ExternalCameraPage.css";
import { useAuth } from "../../context/AuthContext";
import CameraControls from "../../components/Camera/CameraControls";
import SettingsPanel from "../../components/Camera/SettingsPanel";
import CameraDisplay from "../../components/Camera/CameraDisplay";
import HeatmapDisplay from "../../components/Camera/HeatmapDisplay";
import StreamStats from "../../components/Camera/StreamStats";
import TrackingDetails from "../../components/Camera/TrackingDetails";
import AnalyticsGraphs from "../../components/Camera/AnalyticsGraphs";
import Card from "../../components/Layout/Card";

const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000";

/**
 * ExternalCameraPage - Main page with embedded streaming logic
 * Manages WebSocket connection, state, and coordinates sub-components
 */
function ExternalCameraPage() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  // State Management
  const [cameraUrl, setCameraUrl] = useState("http://192.168.1.100:8080/video");
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [fps, setFps] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [selectedModel, setSelectedModel] = useState("yolo-nano");
  const [countHistory, setCountHistory] = useState([]);
  const [fpsHistory, setFpsHistory] = useState([]);
  const [autoSwitch, setAutoSwitch] = useState(false);
  const [autoSwitchThreshold, setAutoSwitchThreshold] = useState(30);
  const [currentAutoModel, setCurrentAutoModel] = useState("yolo-nano");
  const [enableTracking, setEnableTracking] = useState(true);
  const [enableHeatmap, setEnableHeatmap] = useState(true);
  const [showSettings, setShowSettings] = useState(true);

  // Refs
  const imgRef = useRef(null);
  const heatmapRef = useRef(null);
  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Stop streaming
  const stopStream = useCallback(() => {
    setIsStreaming(false);
    setResults(null);
    setFps(0);
    setFrameCount(0);
    disconnectWebSocket();
  }, [disconnectWebSocket]);

  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  const testConnection = async () => {
    try {
      setError(null);
      const res = await fetch(
        `${API_BASE}/camera/test-connection?camera_url=${encodeURIComponent(
          cameraUrl
        )}`
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          data.detail || data.message || "Failed to connect to camera"
        );
      }
      alert(
        `Camera test successful!\nResponse time: ${data.response_time_seconds}s\nImage size: ${data.image_dimensions}`
      );
    } catch (err) {
      console.error("Camera test error:", err);
      setError(`Camera test failed: ${err.message}`);
    }
  };

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(`${WS_BASE}/ws/external-camera`);

      ws.onopen = () => {
        console.log("✅ External camera WebSocket connected");
        setError(null);

        const modelToUse = autoSwitch ? currentAutoModel : selectedModel;

        const connectionData = {
          camera_url: cameraUrl,
          model: modelToUse,
          tracking: enableTracking,
        };

        console.log("📤 Sending connection data:", connectionData);
        ws.send(JSON.stringify(connectionData));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        console.log("📦 Received data:", data);

        if (data.success) {
          if (data.frame) {
            if (imgRef.current) {
              imgRef.current.src = data.frame;
            }
          }

          if (data.heatmap) {
            if (heatmapRef.current) {
              heatmapRef.current.src = data.heatmap;
            }
          }

          if (data.count !== undefined) {
            setResults(data);
            setFps(data.fps || 0);
            setFrameCount(data.frame_number || 0);

            if (data.tracks) {
              console.log(
                "🎯 Tracking data received:",
                data.tracks.length,
                "tracks"
              );
              console.log("Track details:", data.tracks);
            }
            if (data.unique_count !== undefined) {
              console.log("👥 Unique count:", data.unique_count);
            }

            setCountHistory((prev) => [
              ...prev.slice(-49),
              { time: Date.now(), count: data.count },
            ]);
            setFpsHistory((prev) => [
              ...prev.slice(-49),
              { time: Date.now(), fps: data.fps || 0 },
            ]);

            if (autoSwitch) {
              const count = data.count;
              if (
                count < autoSwitchThreshold &&
                !currentAutoModel.startsWith("yolo")
              ) {
                setCurrentAutoModel("yolo-nano");
                console.log(
                  `🔄 Auto-switched to YOLO (count: ${count} < ${autoSwitchThreshold})`
                );
                if (
                  wsRef.current &&
                  wsRef.current.readyState === WebSocket.OPEN
                ) {
                  wsRef.current.send(
                    JSON.stringify({
                      camera_url: cameraUrl,
                      model: "yolo-nano",
                    })
                  );
                }
              } else if (
                count >= autoSwitchThreshold &&
                currentAutoModel.startsWith("yolo")
              ) {
                setCurrentAutoModel("csrnet");
                console.log(
                  `🔄 Auto-switched to CSRNet (count: ${count} >= ${autoSwitchThreshold})`
                );
                if (
                  wsRef.current &&
                  wsRef.current.readyState === WebSocket.OPEN
                ) {
                  wsRef.current.send(
                    JSON.stringify({
                      camera_url: cameraUrl,
                      model: "csrnet",
                    })
                  );
                }
              }
            }
          }
        } else {
          console.error("Processing error:", data.error);
          setError(data.error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("❌ External camera WebSocket disconnected");
        if (isStreaming) {
          setError("Connection lost. Please restart.");
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(`Failed to connect to server: ${err.message}`);
    }
  }, [
    cameraUrl,
    selectedModel,
    isStreaming,
    autoSwitch,
    currentAutoModel,
    enableTracking,
  ]);

  // Request frames from backend
  const requestFrame = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "get_frame" }));
    }
  }, []);

  // Start streaming
  const startStream = useCallback(async () => {
    if (!cameraUrl) {
      setError("Please enter a valid camera URL");
      return;
    }

    console.log("📹 Starting external camera stream");
    console.log("   Camera URL:", cameraUrl);
    console.log("   Model:", selectedModel);

    setLoading(true);
    setError(null);
    stopStream();

    try {
      setIsStreaming(true);
      connectWebSocket();

      intervalRef.current = setInterval(requestFrame, 200);

      setLoading(false);
    } catch (e) {
      console.error("Start stream error:", e);
      setError(e.message);
      stopStream();
      setLoading(false);
    }
  }, [cameraUrl, selectedModel, stopStream, connectWebSocket, requestFrame]);

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access external camera</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div className="external-camera-page">
      {/* Page Header */}
      <header className="external-camera-header">
        <div className="header-left">
          <div className="external-camera-title">
            <h1>📡 External Camera Streaming</h1>
            <p>
              Connect to IP cameras and external feeds for continuous monitoring
            </p>
          </div>
        </div>
        <button className="btn-logout" onClick={logout}>
          Logout
        </button>
      </header>

      {/* Main Content with Card-based Grid Layout */}
      <main className="external-camera-main">
        <div className="webcam-counter-grid">
          {/* Settings Sidebar - Left Column */}
          {/* TODO: SettingsSidebar component deleted - using RightMenu instead */}
          {/*
          <SettingsSidebar
            isStreaming={isStreaming}
            error={error}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            autoSwitch={autoSwitch}
            setAutoSwitch={setAutoSwitch}
            autoSwitchThreshold={autoSwitchThreshold}
            setAutoSwitchThreshold={setAutoSwitchThreshold}
            currentAutoModel={currentAutoModel}
            detectionThreshold={0.5}
            setDetectionThreshold={() => {}}
            enableTracking={enableTracking}
            setEnableTracking={setEnableTracking}
            enableHeatmap={enableHeatmap}
            setEnableHeatmap={setEnableHeatmap}
            showLiveCount={true}
            setShowLiveCount={() => {}}
            showHeatmap={true}
            setShowHeatmap={() => {}}
            showGraph={true}
            setShowGraph={() => {}}
            showMetrics={true}
            setShowMetrics={() => {}}
            onStart={startStream}
            onStop={stopStream}
            fps={fps}
            frameCount={frameCount}
            sourceType="external"
          >
            */}
          {/* Camera URL Input */}
          <div className="setting-group">
            <label>Camera URL</label>
            <input
              type="text"
              value={cameraUrl}
              onChange={(e) => setCameraUrl(e.target.value)}
              placeholder="http://192.168.x.x:8080/video"
              disabled={isStreaming}
            />
            <button
              onClick={testConnection}
              disabled={isStreaming || loading}
              className="btn"
              style={{
                marginTop: "0.5rem",
                background: "#667eea",
                color: "white",
              }}
            >
              Test Connection
            </button>
          </div>
          {/* </SettingsSidebar> */}

          {/* Visualization Grid - Right Column with Cards */}
          <section className="visualization-grid cards-grid">
            {/* Card 1: Live Camera Feed */}
            <Card
              title="📷 External Camera Feed"
              height="450px"
              width="100%"
              showLiveStatus={true}
              isLive={isStreaming}
            >
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "#000",
                  borderRadius: "4px",
                }}
              >
                {isStreaming ? (
                  <img
                    ref={imgRef}
                    alt="External camera stream"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "contain",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      color: "#999",
                      padding: "2rem",
                    }}
                  >
                    <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
                      📷
                    </div>
                    <p>Enter camera URL and click Start Stream</p>
                  </div>
                )}
              </div>
            </Card>

            {/* Card 2: Heatmap Display */}
            <Card title="🔥 Heatmap View" height="450px" width="100%">
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "#000",
                  borderRadius: "4px",
                }}
              >
                {results?.heatmap && enableHeatmap ? (
                  <img
                    ref={heatmapRef}
                    src={results.heatmap}
                    alt="Heatmap"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "contain",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      color: "#999",
                      padding: "2rem",
                    }}
                  >
                    <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
                      🔥
                    </div>
                    <p>
                      {isStreaming
                        ? "Heatmap will appear when available"
                        : "Start streaming to see heatmap"}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Card 3: Count Metrics */}
            <Card title="📊 Count Metrics" height="350px" width="100%">
              <div style={{ padding: "1rem" }}>
                {results ? (
                  <div>
                    <div
                      style={{
                        fontSize: "3rem",
                        fontWeight: "700",
                        color: "#667eea",
                        textAlign: "center",
                        marginBottom: "1rem",
                      }}
                    >
                      {Math.round(results.count || 0)}
                    </div>
                    <div
                      style={{
                        color: "#666",
                        fontSize: "0.9rem",
                        lineHeight: "1.8",
                      }}
                    >
                      <p>
                        <strong>FPS:</strong> {fps.toFixed(1)}
                      </p>
                      <p>
                        <strong>Frame:</strong> {frameCount}
                      </p>
                      <p>
                        <strong>Model:</strong> {currentAutoModel}
                      </p>
                      <p>
                        <strong>Camera URL:</strong>{" "}
                        <span style={{ fontSize: "0.75rem", color: "#999" }}>
                          {cameraUrl.substring(0, 30)}...
                        </span>
                      </p>
                    </div>
                  </div>
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      color: "#999",
                      padding: "2rem",
                    }}
                  >
                    Start streaming to see metrics
                  </div>
                )}
              </div>
            </Card>

            {/* Card 4: Tracking Info */}
            <Card title="🎯 Tracking Info" height="300px" width="100%">
              <div style={{ padding: "1rem" }}>
                <div
                  style={{ color: "#666", fontSize: "0.9rem", lineHeight: "2" }}
                >
                  <p>
                    <strong>Tracking:</strong>{" "}
                    <span
                      style={{
                        color: enableTracking ? "#4ade80" : "#dc2626",
                      }}
                    >
                      {enableTracking ? "ON" : "OFF"}
                    </span>
                  </p>
                  <p>
                    <strong>Auto-Switch:</strong>{" "}
                    <span style={{ color: autoSwitch ? "#4ade80" : "#dc2626" }}>
                      {autoSwitch ? "ON" : "OFF"}
                    </span>
                  </p>
                  <p>
                    <strong>Current Model:</strong> {currentAutoModel}
                  </p>
                  <p>
                    <strong>Heatmap:</strong>{" "}
                    <span
                      style={{
                        color: enableHeatmap ? "#4ade80" : "#dc2626",
                      }}
                    >
                      {enableHeatmap ? "ENABLED" : "DISABLED"}
                    </span>
                  </p>
                </div>
              </div>
            </Card>

            {/* Card 5: Stream Status */}
            <Card
              title="🔴 Stream Status"
              height="300px"
              width="100%"
              metrics={[
                { label: "Status", value: isStreaming ? "ACTIVE" : "IDLE" },
                { label: "FPS", value: fps.toFixed(1) },
                { label: "Frame", value: frameCount },
              ]}
              showMetrics={true}
            >
              <div style={{ padding: "1rem" }}>
                {error && (
                  <div
                    style={{
                      padding: "1rem",
                      background: "#fee2e2",
                      border: "1px solid #fca5a5",
                      borderRadius: "4px",
                      color: "#dc2626",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>Error:</strong> {error}
                  </div>
                )}
                {!error && isStreaming && (
                  <div
                    style={{
                      padding: "1rem",
                      background: "#dcfce7",
                      border: "1px solid #86efac",
                      borderRadius: "4px",
                      color: "#166534",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>✓</strong> External camera stream is active
                  </div>
                )}
                {!error && !isStreaming && (
                  <div
                    style={{
                      padding: "1rem",
                      background: "#fef3c7",
                      border: "1px solid #fcd34d",
                      borderRadius: "4px",
                      color: "#92400e",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>⚠</strong> Stream is not active. Enter camera URL
                    and click Start Stream.
                  </div>
                )}
                {loading && (
                  <div
                    style={{
                      padding: "1rem",
                      background: "#dbeafe",
                      border: "1px solid #93c5fd",
                      borderRadius: "4px",
                      color: "#1e40af",
                      fontSize: "0.9rem",
                    }}
                  >
                    <strong>⏳</strong> Connecting to camera...
                  </div>
                )}
              </div>
            </Card>
          </section>
        </div>
      </main>
    </div>
  );
}

export default ExternalCameraPage;
