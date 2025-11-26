import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/WebcamPage.css";
import { useAuth } from "../../context/AuthContext";
import { useWebcam } from "../../context/WebcamContext";
import CSRNetCard from "../../components/Models/CSRNet/CSRNetCard";
import HeatmapCard from "../../components/Models/CSRNet/HeatmapCard";
import Nav from "../../components/Nav/Nav";
import Menu from "../../components/Menu/Menu";
import RightMenu from "../../components/Menu/RightMenu";
import WebcamControlPanel from "../../components/Webcam/WebcamControlPanel";
import WebcamTrajectoryPanel from "../../components/Trajectory/WebcamTrajectoryPanel";
import TrajectoryLegendPanel from "../../components/Trajectory/TrajectoryLegendPanel";
import WebcamMetricsChart from "../../components/Webcam/WebcamMetricsChart";
import {
  TrajectoryTrackingPanel,
  StatusPanel,
  StreamStatsBar,
} from "../../components/shared";

function Webcam() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Local state for layout
  const [isMenuOpen, setIsMenuOpen] = useState(true);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [mode, setMode] = useState("dashboard");
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("info"); // success, danger, warning, info

  // Get all webcam state and functions from context
  const {
    isStreaming,
    selectedModel,
    enableHeatmap,
    enableTracking,
    count,
    fps,
    inferenceTime,
    status,
    error,
    results,
    heatmapImage,
    annotatedFrame, // ML-processed frame with bounding boxes & trajectories
    densityStats,
    metricsHistory,
    notification,
    videoRef,
    canvasRef,
    wsRef,
    stopEverything,
  } = useWebcam();

  const densityModelActive = ["csrnet", "vmamba", "tmtb"].includes(
    (selectedModel || "").toLowerCase()
  );
  const isYoloSelected = (selectedModel || "").toLowerCase().includes("yolo");
  const backendModelName = (results?.model || "").toLowerCase();
  const isYoloFromBackend = backendModelName.includes("yolo");
  const yoloActive = isYoloSelected || isYoloFromBackend;
  const hasBackendTracks =
    Array.isArray(results?.tracks) && results.tracks.length > 0;
  const trackingActive = enableTracking || hasBackendTracks;
  const trajectoryTracks = results?.tracks || [];

  // Show annotated frame from ML when tracking is active
  const showAnnotatedFrame =
    isStreaming && yoloActive && trackingActive && annotatedFrame;

  // Debug trajectory rendering
  console.log("🚶 Trajectory Debug:", {
    isStreaming,
    yoloActive,
    trackingActive,
    hasAnnotatedFrame: !!annotatedFrame,
    numTracks: trajectoryTracks.length,
  });

  // Cleanup on unmount ONLY - ✅ FIX: Empty deps to prevent re-running
  useEffect(() => {
    return () => {
      console.log("🧹 Webcam component unmounting - cleaning up");
      stopEverything();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // ✅ Empty array - cleanup only on unmount

  // Toast notification effect - show errors/status changes
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
    } else if (status === "Streaming...") {
      setToastMessage("Webcam streaming started successfully!");
      setToastType("success");
      setShowToast(true);
      timeoutId = setTimeout(() => setShowToast(false), 3000);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [error, status, notification]);

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
      className="app-layout"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Bootstrap Toast Notification */}
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

      {/* PART 1: NAVIGATION BAR - TOP (Full Width) */}
      <div className="layout-nav-bar">
        <Nav mode={mode} setMode={setMode} />
      </div>

      {/* PART 2, 3 & 4: MAIN CONTAINER (Left Sidebar + Content + Right Menu) */}
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

        {/* PART 3: MAIN CONTENT AREA (Center) */}
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
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              textAlign: "center",
              marginBottom: "2rem",
            }}
          >
            <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
              📹 Live Webcam Feed
            </h1>
            <p style={{ fontSize: "1rem", opacity: 0.9 }}>
              Real-time crowd detection using CSRNet
            </p>
          </header>

          {/* Main Content */}
          <div style={{ padding: "0 2rem" }}>
            <WebcamControlPanel />

            {/* Status Panel - Using shared component */}
            <StatusPanel
              status={status}
              isStreaming={isStreaming}
              wsState={wsRef.current?.readyState}
              selectedModel={selectedModel}
              count={count}
              fps={fps}
              inferenceTime={inferenceTime}
              additionalInfo={{
                Webcam:
                  videoRef.current?.readyState === 2
                    ? "✅ Ready"
                    : `State ${videoRef.current?.readyState || "N/A"}`,
              }}
            />

            <WebcamMetricsChart history={metricsHistory} />

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

            {/* Video & Heatmap Display */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
                gap: "1.5rem",
                marginBottom: "2rem",
              }}
            >
              <div
                style={{
                  background: "white",
                  borderRadius: "12px",
                  padding: "1.5rem",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                }}
              >
                <h3 style={{ margin: "0 0 1rem 0" }}>📹 Live Feed</h3>
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
                  {/* Always show raw video in Live Feed panel */}
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
                  {isStreaming && (
                    <div
                      style={{
                        position: "absolute",
                        top: "12px",
                        left: "12px",
                        background: "rgba(15,23,42,0.85)",
                        color: "white",
                        padding: "0.4rem 0.75rem",
                        borderRadius: "8px",
                        fontWeight: 600,
                        letterSpacing: "0.05em",
                        fontSize: "0.95rem",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
                      }}
                    >
                      Count: {Number.isFinite(count) ? count.toFixed(2) : "--"}
                    </div>
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
                        fontSize: "1.5rem",
                        fontWeight: "600",
                        textAlign: "center",
                        padding: "1rem",
                      }}
                    >
                      Click "Start System" in the control panel above
                    </div>
                  )}
                </div>
                <canvas ref={canvasRef} style={{ display: "none" }} />

                {/* Stats Display */}
                {isStreaming && (
                  <div
                    style={{
                      marginTop: "1rem",
                      padding: "1rem",
                      background: "#f9fafb",
                      borderRadius: "8px",
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(150px, 1fr))",
                      gap: "1rem",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                        Count
                      </div>
                      <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>
                        {count}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                        FPS
                      </div>
                      <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>
                        {fps.toFixed(1)}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                        Inference
                      </div>
                      <div style={{ fontSize: "1.5rem", fontWeight: "700" }}>
                        {inferenceTime.toFixed(0)}ms
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Heatmap Panel - Only show for density models (CSRNet, VMamba, TMTB) */}
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
                      alignSelf: "stretch",
                    }}
                  >
                    💡 Enable "Show Heatmap" in the control panel to see density
                    visualization.
                  </div>
                ))}

              {/* Trajectory Tracking Panel - Using shared component */}
              <TrajectoryTrackingPanel
                annotatedFrame={annotatedFrame}
                trackCount={trajectoryTracks.length}
                isVisible={showAnnotatedFrame}
              />
            </div>

            {/* Modular Components for Results Display */}
            {isStreaming && results && (
              <div style={{ display: "grid", gap: "2rem" }}>
                {/* CSRNet Results Card */}
                <CSRNetCard
                  results={results}
                  loading={false}
                  error={null}
                  title={`${selectedModel} Live Results`}
                  showRawJson={true}
                  showHeatmap={false}
                />

                {/* Debug Info */}
                <div
                  style={{
                    padding: "1rem",
                    background: "#f0f9ff",
                    borderRadius: "8px",
                    fontFamily: "monospace",
                    fontSize: "0.85rem",
                  }}
                >
                  <strong>🐛 Debug:</strong>
                  <br />
                  enableHeatmap: {enableHeatmap ? "✅ true" : "❌ false"}
                  <br />
                  heatmapImage exists: {heatmapImage ? "✅ yes" : "❌ no"}
                  <br />
                  {heatmapImage &&
                    `heatmapImage length: ${heatmapImage.length} chars`}
                </div>

                <WebcamTrajectoryPanel
                  isActive={yoloActive && trackingActive}
                  tracks={trajectoryTracks}
                  uniqueCount={results?.unique_count || results?.count}
                />

                {/* Trajectory Visualization Controls */}
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
                      <li>Unique colored bounding boxes per person</li>
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

                {/* Density Statistics */}
                {densityStats && (
                  <div
                    style={{
                      background: "white",
                      borderRadius: "12px",
                      padding: "1.5rem",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                    }}
                  >
                    <h3 style={{ margin: "0 0 1rem 0" }}>
                      📊 Density Map Statistics
                    </h3>
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "repeat(auto-fit, minmax(200px, 1fr))",
                        gap: "1rem",
                      }}
                    >
                      <div>
                        <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                          Min Density
                        </div>
                        <div style={{ fontSize: "1.2rem", fontWeight: "600" }}>
                          {densityStats.min?.toFixed(4) || "N/A"}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                          Max Density
                        </div>
                        <div style={{ fontSize: "1.2rem", fontWeight: "600" }}>
                          {densityStats.max?.toFixed(4) || "N/A"}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                          Mean Density
                        </div>
                        <div style={{ fontSize: "1.2rem", fontWeight: "600" }}>
                          {densityStats.mean?.toFixed(4) || "N/A"}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: "0.85rem", color: "#6b7280" }}>
                          Sum
                        </div>
                        <div style={{ fontSize: "1.2rem", fontWeight: "600" }}>
                          {densityStats.sum?.toFixed(2) || "N/A"}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
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

export default Webcam;
