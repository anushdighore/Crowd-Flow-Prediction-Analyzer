import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/WebcamPage.css"; // Reuse webcam styles
import { useAuth } from "../../context/AuthContext";
import { useExternalCamera } from "../../context/ExternalCameraContext";
import CSRNetCard from "../../components/Models/CSRNet/CSRNetCard";
import HeatmapCard from "../../components/Models/CSRNet/HeatmapCard";
import Nav from "../../components/Nav/Nav";
import Menu from "../../components/Menu/Menu";
import RightMenu from "../../components/Menu/RightMenu";
import WebcamTrajectoryPanel from "../../components/Trajectory/WebcamTrajectoryPanel";
import TrajectoryLegendPanel from "../../components/Trajectory/TrajectoryLegendPanel";
import {
  LiveFeedPanel,
  TrajectoryTrackingPanel,
  StatusPanel,
  StreamStatsBar,
} from "../../components/shared";

/**
 * ExternalCamera - External camera streaming page with trajectory tracking
 * Uses ExternalCameraContext for state management
 * Shares layout and components with Webcam page
 */
function ExternalCamera() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Local state for layout
  const [isMenuOpen, setIsMenuOpen] = useState(true);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [mode, setMode] = useState("dashboard");
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("info");

  // Get all external camera state from context
  const {
    isStreaming,
    loading,
    cameraUrl,
    selectedModel,
    enableTracking,
    enableHeatmap,
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
    handleStartStreaming,
    handleStopStreaming,
    testConnection,
    stopEverything,
  } = useExternalCamera();

  // Debug logging
  useEffect(() => {
    console.log("🎥 External Camera Debug:", {
      isStreaming,
      yoloActive,
      trackingActive,
      hasAnnotatedFrame: !!annotatedFrame,
      numTracks: trajectoryTracks.length,
    });
  }, [
    isStreaming,
    yoloActive,
    trackingActive,
    annotatedFrame,
    trajectoryTracks,
  ]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log("🧹 External Camera component unmounting - cleaning up");
      stopEverything();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Toast notification effect
  useEffect(() => {
    let timeoutId;

    if (notification) {
      setToastMessage(notification.message);
      setToastType(notification.type || "info");
      setShowToast(true);
      timeoutId = setTimeout(() => setShowToast(false), 4000);
      return () => clearTimeout(timeoutId);
    }

    if (error) {
      setToastMessage(error);
      setToastType("danger");
      setShowToast(true);
      timeoutId = setTimeout(() => setShowToast(false), 5000);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [error, notification]);

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access external camera</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div
      className="app-layout"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Toast Notification */}
      {showToast && (
        <div
          style={{
            position: "fixed",
            top: "20px",
            right: "20px",
            zIndex: 9999,
            minWidth: "300px",
            maxWidth: "500px",
          }}
        >
          <div
            className={`alert alert-${toastType} alert-dismissible fade show`}
            role="alert"
            style={{
              boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              borderRadius: "8px",
            }}
          >
            <strong>
              {toastType === "danger" && "⚠️ Error: "}
              {toastType === "success" && "✅ Success: "}
              {toastType === "warning" && "⚡ Warning: "}
              {toastType === "info" && "ℹ️ Info: "}
            </strong>
            {toastMessage}
            <button
              type="button"
              className="btn-close"
              onClick={() => setShowToast(false)}
              aria-label="Close"
            ></button>
          </div>
        </div>
      )}

      {/* PART 1: NAVIGATION BAR */}
      <div className="layout-nav-bar">
        <Nav mode={mode} setMode={setMode} />
      </div>

      {/* PART 2, 3 & 4: MAIN CONTAINER */}
      <div
        className="layout-main-container"
        style={{
          display: "flex",
          flex: 1,
          overflow: "hidden",
          paddingRight: isRightMenuOpen ? "280px" : "0px",
          transition: "padding-right 0.3s ease",
        }}
      >
        {/* PART 2: SIDEBAR MENU (Left) */}
        <div className={`layout-sidebar ${isMenuOpen ? "menu-open" : ""}`}>
          <Menu
            isOpen={isMenuOpen}
            onClose={() => setIsMenuOpen(false)}
            onToggle={() => setIsMenuOpen(!isMenuOpen)}
          />
        </div>

        {/* PART 3: MAIN CONTENT AREA */}
        <main
          className="layout-content"
          style={{
            flex: 1,
            overflowY: "auto",
            paddingRight: "2rem",
            transition: "all 0.3s ease",
          }}
        >
          {/* Header */}
          <header
            style={{
              padding: "2rem",
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              color: "white",
              textAlign: "center",
              marginBottom: "2rem",
            }}
          >
            <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
              📡 External Camera Feed
            </h1>
            <p style={{ fontSize: "1rem", opacity: 0.9 }}>
              Connect to IP cameras and external feeds for crowd monitoring
            </p>
          </header>

          {/* Main Content */}
          <div style={{ padding: "0 2rem" }}>
            {/* Camera URL Input & Controls */}
            <div
              style={{
                background: "white",
                borderRadius: "12px",
                padding: "1.5rem",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                marginBottom: "2rem",
              }}
            >
              <h3 style={{ margin: "0 0 1rem 0" }}>🎛️ Camera Settings</h3>

              {/* Camera URL Input */}
              <div style={{ marginBottom: "1rem" }}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "0.5rem",
                    fontWeight: 600,
                  }}
                >
                  Camera URL
                </label>
                <input
                  type="text"
                  value={cameraUrl}
                  onChange={(e) => setCameraUrl(e.target.value)}
                  placeholder="http://192.168.1.100:8080/video"
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid #d1d5db",
                    fontSize: "0.9rem",
                  }}
                  disabled={isStreaming}
                />
              </div>

              {/* Toggles */}
              <div
                style={{
                  display: "flex",
                  gap: "2rem",
                  marginBottom: "1rem",
                  flexWrap: "wrap",
                }}
              >
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    cursor: "pointer",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={enableTracking}
                    onChange={(e) => setEnableTracking(e.target.checked)}
                  />
                  <span>Enable Tracking</span>
                </label>
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    cursor: "pointer",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={enableHeatmap}
                    onChange={(e) => setEnableHeatmap(e.target.checked)}
                  />
                  <span>Enable Heatmap</span>
                </label>
              </div>

              {/* Control Buttons */}
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                <button
                  onClick={testConnection}
                  disabled={isStreaming || loading}
                  style={{
                    padding: "0.75rem 1.5rem",
                    borderRadius: "8px",
                    border: "none",
                    background: "#6366f1",
                    color: "white",
                    fontWeight: 600,
                    cursor: isStreaming || loading ? "not-allowed" : "pointer",
                    opacity: isStreaming || loading ? 0.6 : 1,
                  }}
                >
                  🔍 Test Connection
                </button>

                {!isStreaming ? (
                  <button
                    onClick={handleStartStreaming}
                    disabled={loading || !cameraUrl}
                    style={{
                      padding: "0.75rem 1.5rem",
                      borderRadius: "8px",
                      border: "none",
                      background: "#10b981",
                      color: "white",
                      fontWeight: 600,
                      cursor: loading || !cameraUrl ? "not-allowed" : "pointer",
                      opacity: loading || !cameraUrl ? 0.6 : 1,
                    }}
                  >
                    {loading ? "⏳ Connecting..." : "▶️ Start Stream"}
                  </button>
                ) : (
                  <button
                    onClick={handleStopStreaming}
                    style={{
                      padding: "0.75rem 1.5rem",
                      borderRadius: "8px",
                      border: "none",
                      background: "#ef4444",
                      color: "white",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    ⏹️ Stop Stream
                  </button>
                )}
              </div>
            </div>

            {/* Status Panel */}
            <StatusPanel
              status={status}
              isStreaming={isStreaming}
              wsState={wsRef.current?.readyState}
              selectedModel={selectedModel}
              count={count}
              fps={fps}
              inferenceTime={inferenceTime}
              additionalInfo={{
                Frame: frameCount,
                Camera: cameraUrl.substring(0, 30) + "...",
              }}
            />

            {/* Error Display */}
            {error && (
              <div
                style={{
                  padding: "1rem",
                  background: "#fee2e2",
                  border: "2px solid #ef4444",
                  borderRadius: "8px",
                  color: "#dc2626",
                  marginBottom: "2rem",
                }}
              >
                <strong>⚠️ Error:</strong> {error}
              </div>
            )}

            {/* Video & Visualization Grid */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
                gap: "1.5rem",
                marginBottom: "2rem",
              }}
            >
              {/* Live Feed Panel */}
              <div>
                <LiveFeedPanel
                  imgRef={imgRef}
                  isStreaming={isStreaming}
                  count={count}
                  title="📷 External Camera Feed"
                  placeholderText="Enter camera URL and click Start Stream"
                  feedType="image"
                />
                {isStreaming && (
                  <StreamStatsBar
                    count={count}
                    fps={fps}
                    inferenceTime={inferenceTime}
                    additionalStats={[{ label: "Frame", value: frameCount }]}
                  />
                )}
              </div>

              {/* Heatmap Panel - Only for density models */}
              {isStreaming &&
                results &&
                densityModelActive &&
                (enableHeatmap ? (
                  <div
                    style={{
                      background: "white",
                      borderRadius: "12px",
                      padding: "1.5rem",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                    }}
                  >
                    <HeatmapCard
                      heatmapImage={heatmapImage}
                      count={count}
                      inferenceTime={inferenceTime}
                      isLoading={isStreaming && !heatmapImage}
                      title={`${selectedModel} Density Heatmap`}
                      showOriginalImage={false}
                      enableHeatmap={enableHeatmap}
                      selectedModel={selectedModel}
                    />
                  </div>
                ) : (
                  <div
                    style={{
                      padding: "1.5rem",
                      background: "#fef3c7",
                      borderRadius: "12px",
                      border: "1px dashed #fbbf24",
                      alignSelf: "start",
                    }}
                  >
                    💡 Enable "Show Heatmap" to see density visualization.
                  </div>
                ))}

              {/* Trajectory Tracking Panel - Only for YOLO with tracking */}
              <TrajectoryTrackingPanel
                annotatedFrame={annotatedFrame}
                trackCount={trajectoryTracks.length}
                isVisible={showAnnotatedFrame}
              />
            </div>

            {/* Results Section */}
            {isStreaming && results && (
              <div style={{ display: "grid", gap: "2rem" }}>
                {/* Results Card */}
                <CSRNetCard
                  results={results}
                  loading={false}
                  error={null}
                  title={`${selectedModel} Live Results`}
                  showRawJson={true}
                  showHeatmap={false}
                />

                {/* Trajectory Panel */}
                <WebcamTrajectoryPanel
                  isActive={yoloActive && trackingActive}
                  tracks={trajectoryTracks}
                  uniqueCount={results?.unique_count || results?.count}
                />

                {/* Trajectory Visualization Info */}
                {yoloActive && trackingActive && (
                  <div
                    style={{
                      background: "white",
                      borderRadius: "12px",
                      padding: "1.5rem",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                    }}
                  >
                    <h3 style={{ margin: "0 0 1rem 0" }}>
                      🎨 Path Visualization
                    </h3>
                    <p
                      style={{
                        fontSize: "0.9rem",
                        color: "#475569",
                        margin: "0 0 0.75rem 0",
                      }}
                    >
                      Visualization is processed by the ML layer and includes:
                    </p>
                    <ul
                      style={{
                        margin: 0,
                        paddingLeft: "1.25rem",
                        color: "#64748b",
                        fontSize: "0.85rem",
                      }}
                    >
                      <li>Unique colored markers per person</li>
                      <li>Track ID labels with speed indicators</li>
                      <li>Trajectory paths (gradient - older points fade)</li>
                      <li>Predicted movement paths (dashed lines)</li>
                    </ul>
                  </div>
                )}

                {/* Trajectory Legend Panel */}
                <TrajectoryLegendPanel
                  tracks={trajectoryTracks}
                  isActive={yoloActive && trackingActive}
                />
              </div>
            )}
          </div>
        </main>

        {/* PART 4: RIGHT CONTROL MENU */}
        <RightMenu
          isOpen={isRightMenuOpen}
          onToggle={() => setIsRightMenuOpen((prev) => !prev)}
        />
      </div>
    </div>
  );
}

export default ExternalCamera;
