import React, { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/WebcamPage.css";
import "../../styles/WebcamCounterNew.css";
import { useAuth } from "../../context/AuthContext";
import {
  LiveFeedCard,
  HeatmapCard,
  MetricsCard,
  GraphCard,
} from "../../components/Visualization";
import LiveCameraFeedCard from "../../components/Camera/LiveCameraFeedCard";
import Card from "../../components/Layout/Card";

function Webcam() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // State Management
  const [isStreaming, setIsStreaming] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [fps, setFps] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [selectedModel, setSelectedModel] = useState("yolo-nano");
  const [enableTracking, setEnableTracking] = useState(false);
  const [enableHeatmap, setEnableHeatmap] = useState(false);
  const [uniqueCount, setUniqueCount] = useState(0);
  const [heatmapImage, setHeatmapImage] = useState(null);
  const [autoSwitch, setAutoSwitch] = useState(false);
  const [autoSwitchThreshold, setAutoSwitchThreshold] = useState(30);
  const [currentAutoModel, setCurrentAutoModel] = useState("yolo-nano");
  const [detectionThreshold, setDetectionThreshold] = useState(0.5);
  const [showLiveCount, setShowLiveCount] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showGraph, setShowGraph] = useState(true);
  const [showMetrics, setShowMetrics] = useState(true);
  const [countHistory, setCountHistory] = useState([]);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [rightMenuSelectedModel, setRightMenuSelectedModel] =
    useState("CSRNet");
  const [rightMenuSettings, setRightMenuSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Start webcam
  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }

      setError(null);
    } catch (err) {
      setError(`Failed to access webcam: ${err.message}`);
      console.error("Webcam error:", err);
    }
  }, []);

  // Stop webcam
  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket("ws://localhost:8000/ws/count");

      ws.onopen = () => {
        console.log("✅ WebSocket connected");
        setError(null);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.success) {
          setResults(data);
          setFps(data.fps || 0);
          setFrameCount(data.frame_number || 0);

          // Update count history for graph
          setCountHistory((prev) => {
            const newHistory = [
              ...prev,
              { time: Date.now(), count: data.count || 0 },
            ];
            return newHistory.slice(-30);
          });

          // Update unique count if tracking is enabled
          if (enableTracking && data.unique_count !== undefined) {
            setUniqueCount(data.unique_count);
          }

          // Update heatmap if enabled
          if (enableHeatmap && data.heatmap) {
            setHeatmapImage(data.heatmap);
          }

          // Auto-switch logic based on count
          if (autoSwitch && data.count !== undefined) {
            const count = data.count;
            if (
              count < autoSwitchThreshold &&
              !currentAutoModel.startsWith("yolo")
            ) {
              setCurrentAutoModel("yolo-nano");
            } else if (
              count >= autoSwitchThreshold &&
              currentAutoModel.startsWith("yolo")
            ) {
              setCurrentAutoModel("csrnet");
            }
          }
        } else {
          console.error("Processing error:", data.error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("❌ WebSocket disconnected");
        if (isStreaming) {
          setError("Connection lost. Please restart.");
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(`Failed to connect to server: ${err.message}`);
    }
  }, [
    isStreaming,
    enableTracking,
    enableHeatmap,
    autoSwitch,
    autoSwitchThreshold,
    currentAutoModel,
  ]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Capture and send frame
  const captureAndSendFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current) {
      return;
    }

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const frameData = canvas.toDataURL("image/jpeg", 0.8);

      const modelToUse = autoSwitch ? currentAutoModel : selectedModel;

      wsRef.current.send(
        JSON.stringify({
          frame: frameData,
          model: modelToUse,
          tracking: enableTracking,
          heatmap: enableHeatmap,
          threshold: detectionThreshold,
        })
      );
    } catch (err) {
      console.error("Frame capture error:", err);
    }
  }, [
    selectedModel,
    enableTracking,
    enableHeatmap,
    autoSwitch,
    currentAutoModel,
    detectionThreshold,
  ]);

  // Start streaming
  const handleStartStreaming = async () => {
    await startWebcam();
    connectWebSocket();

    intervalRef.current = setInterval(captureAndSendFrame, 100);

    setIsStreaming(true);
    setResults(null);
    setCountHistory([]);
  };

  // Stop streaming
  const handleStopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    disconnectWebSocket();
    stopWebcam();

    setIsStreaming(false);
    setResults(null);
    setFps(0);
    setFrameCount(0);
    setUniqueCount(0);
    setHeatmapImage(null);
    setCountHistory([]);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      disconnectWebSocket();
      stopWebcam();
    };
  }, [disconnectWebSocket, stopWebcam]);

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access the webcam</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      <main
        className="webcam-main"
        style={{
          flex: 1,
          overflowY: "auto",
          paddingRight: isRightMenuOpen ? "320px" : "50px",
          transition: "all 0.3s ease",
        }}
      >
        <div className="webcam-counter-grid">
          {/* Visualization Grid - Main Column */}
          <section className="visualization-grid cards-grid">
            {/* Card 1: Live Camera Feed */}
            <Card
              title="📹 Live Camera Feed"
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
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "contain",
                  }}
                />
              </div>
            </Card>

            {/* Card 2: Count Metrics */}
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

            {/* Card 3: Tracking Info */}
            <Card title="🎯 Tracking Info" height="300px" width="100%">
              <div style={{ padding: "1rem" }}>
                <div
                  style={{ color: "#666", fontSize: "0.9rem", lineHeight: "2" }}
                >
                  <p>
                    <strong>Tracking:</strong>{" "}
                    <span
                      style={{ color: enableTracking ? "#4ade80" : "#dc2626" }}
                    >
                      {enableTracking ? "ON" : "OFF"}
                    </span>
                  </p>
                  <p>
                    <strong>Unique Count:</strong> {uniqueCount}
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
                </div>
              </div>
            </Card>

            {/* Card 4: Detection Settings */}
            <Card title="⚙️ Detection Settings" height="300px" width="100%">
              <div style={{ padding: "1rem" }}>
                <div
                  style={{ color: "#666", fontSize: "0.9rem", lineHeight: "2" }}
                >
                  <p>
                    <strong>Selected Model:</strong> {selectedModel}
                  </p>
                  <p>
                    <strong>Detection Threshold:</strong>{" "}
                    {(detectionThreshold * 100).toFixed(0)}%
                  </p>
                  <p>
                    <strong>Auto-Switch Threshold:</strong>{" "}
                    {autoSwitchThreshold}
                  </p>
                  <p>
                    <strong>Heatmap:</strong>{" "}
                    <span
                      style={{ color: enableHeatmap ? "#4ade80" : "#dc2626" }}
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
                    <strong>✓</strong> Stream is active and running smoothly
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
                    <strong>⚠</strong> Stream is not active
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

export default Webcam;
