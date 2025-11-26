import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../../context/AuthContext";
import { useExternalCamera } from "../../context/ExternalCameraContext";
import { useTheme } from "../../context/ThemeContext";
import Nav from "../../components/Nav/Nav";
import Menu from "../../components/Menu/Menu";
import MainRightMenu from "../../components/Menu/MainRightMenu";
import LiveFeedPanel from "../../components/shared/LiveFeedPanel";
import StatusPanel from "../../components/shared/StatusPanel";
import StreamStatsBar from "../../components/shared/StreamStatsBar";
import HeatmapCard from "../../components/Models/CSRNet/HeatmapCard";
import TrajectoryTrackingPanel from "../../components/shared/TrajectoryTrackingPanel";
import CSRNetCard from "../../components/Models/CSRNet/CSRNetCard";
import WebcamTrajectoryPanel from "../../components/Trajectory/WebcamTrajectoryPanel";
import TrajectoryLegendPanel from "../../components/Trajectory/TrajectoryLegendPanel";
import OccupancyWidget from "../../components/occupancy/OccupancyWidget";

/**
 * Main.js - Standalone Page with Manual Layout
 * This page does NOT use the Layout component.
 * It manually includes Nav + Left Menu + Right Menu for full control.
 */
function Main() {
  const { isAuthenticated } = useAuth();
  const { isDarkMode } = useTheme();

  // Menu states
  const [isMenuOpen, setIsMenuOpen] = useState(true);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);

  // Nav mode state (required by Nav component)
  const [mode, setMode] = useState("dashboard");

  // Occupancy state
  const [occupancyData, setOccupancyData] = useState(null);
  const [alertData, setAlertData] = useState(null);
  const [densityHeatmap, setDensityHeatmap] = useState(null);
  const [occupancyStatistics, setOccupancyStatistics] = useState(null);
  const [occupancyAlerts, setOccupancyAlerts] = useState([]);
  const [historicalDataAvailable, setHistoricalDataAvailable] = useState(false);
  const [occupancyTimestamp, setOccupancyTimestamp] = useState(null);

  // Toast notification state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("info"); // info, success, warning, danger
  const lastShownAlertTimestamp = useRef(null); // Track last shown alert to avoid duplicates

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

  // Update occupancy data when results change
  useEffect(() => {
    if (results) {
      // Extract occupancy data from results
      if (results.occupancy) {
        setOccupancyData(results.occupancy);
      }

      // Extract alert data if present
      if (results.alert) {
        setAlertData(results.alert);
      } else {
        setAlertData(null);
      }

      // Extract enhanced occupancy fields
      if (results.density_heatmap) {
        setDensityHeatmap(results.density_heatmap);
      }

      if (results.occupancy_statistics) {
        setOccupancyStatistics(results.occupancy_statistics);
      }

      // Check both occupancy_alerts directly and alerts inside occupancy object
      if (results.occupancy_alerts && results.occupancy_alerts.length > 0) {
        console.log("📢 New occupancy alerts received:", results.occupancy_alerts);
        setOccupancyAlerts(results.occupancy_alerts);
      } else if (results.occupancy?.alerts && results.occupancy.alerts.length > 0) {
        console.log("📢 New occupancy alerts from occupancy object:", results.occupancy.alerts);
        setOccupancyAlerts(results.occupancy.alerts);
      }

      if (results.historical_data_available !== undefined) {
        setHistoricalDataAvailable(results.historical_data_available);
      }

      if (results.occupancy_timestamp) {
        setOccupancyTimestamp(results.occupancy_timestamp);
      }
    } else {
      setOccupancyData(null);
      setAlertData(null);
      setDensityHeatmap(null);
      setOccupancyStatistics(null);
      setOccupancyAlerts([]);
      setHistoricalDataAvailable(false);
      setOccupancyTimestamp(null);
    }
  }, [results]);

  // Toast notification effect for occupancy alerts
  useEffect(() => {
    let timeoutId;

    // Show toast for NEW occupancy alerts only
    if (occupancyAlerts && occupancyAlerts.length > 0) {
      const latestAlert = occupancyAlerts[occupancyAlerts.length - 1];
      const alertTimestamp = latestAlert.timestamp;
      
      console.log("🔔 Toast check - Latest alert:", latestAlert);
      console.log("🔔 Last shown timestamp:", lastShownAlertTimestamp.current);
      
      // Only show toast if this is a NEW alert (different timestamp)
      if (alertTimestamp && alertTimestamp !== lastShownAlertTimestamp.current) {
        lastShownAlertTimestamp.current = alertTimestamp;
        
        const alertLevel = latestAlert.level || "warning";

        // Map alert levels to toast types
        const typeMap = {
          critical: "danger",
          warning: "warning",
          info: "info",
          success: "success",
        };

        console.log("🍞 Showing toast for alert:", latestAlert.message, "Level:", alertLevel);
        
        setToastMessage(latestAlert.message || "Occupancy alert triggered");
        setToastType(typeMap[alertLevel] || "warning");
        setShowToast(true);

        // Play sound for critical alerts (optional)
        if (alertLevel === "critical") {
          console.log("🚨 CRITICAL OCCUPANCY ALERT:", latestAlert.message);
        }

        timeoutId = setTimeout(() => setShowToast(false), 5000);
      }
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [occupancyAlerts]);

  // Separate useEffect for error notifications
  useEffect(() => {
    let timeoutId;
    if (error) {
      setToastMessage(error);
      setToastType("danger");
      setShowToast(true);
      timeoutId = setTimeout(() => setShowToast(false), 5000);
    }
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [error]);

  // Separate useEffect for general notifications  
  useEffect(() => {
    let timeoutId;
    if (notification) {
      setToastMessage(notification.message);
      setToastType(notification.type || "info");
      setShowToast(true);
      timeoutId = setTimeout(() => setShowToast(false), 4000);
    }
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [notification]);

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access the main page</p>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
        backgroundColor: "var(--bg-primary)",
      }}
    >
      {/* Toast Notification for Occupancy Alerts */}
      {showToast && (
        <div
          style={{
            position: "fixed",
            top: "80px",
            right: "20px",
            zIndex: 9999,
            minWidth: "320px",
            maxWidth: "450px",
            animation: "slideIn 0.3s ease-out",
          }}
        >
          <div
            style={{
              background: isDarkMode
                ? toastType === "danger"
                  ? "linear-gradient(135deg, #dc3545 0%, #c82333 100%)"
                  : toastType === "warning"
                  ? "linear-gradient(135deg, #ffc107 0%, #e0a800 100%)"
                  : toastType === "success"
                  ? "linear-gradient(135deg, #28a745 0%, #1e7e34 100%)"
                  : "linear-gradient(135deg, #17a2b8 0%, #138496 100%)"
                : toastType === "danger"
                ? "#fee2e2"
                : toastType === "warning"
                ? "#fef3c7"
                : toastType === "success"
                ? "#d1fae5"
                : "#dbeafe",
              color: isDarkMode
                ? "#ffffff"
                : toastType === "danger"
                ? "#991b1b"
                : toastType === "warning"
                ? "#92400e"
                : toastType === "success"
                ? "#065f46"
                : "#1e40af",
              padding: "1rem 1.25rem",
              borderRadius: "12px",
              boxShadow: isDarkMode
                ? "0 10px 25px rgba(0, 0, 0, 0.5)"
                : "0 10px 25px rgba(0, 0, 0, 0.15)",
              display: "flex",
              alignItems: "flex-start",
              gap: "0.75rem",
              border: isDarkMode
                ? "none"
                : `1px solid ${
                    toastType === "danger"
                      ? "#fca5a5"
                      : toastType === "warning"
                      ? "#fcd34d"
                      : toastType === "success"
                      ? "#6ee7b7"
                      : "#93c5fd"
                  }`,
            }}
          >
            <span style={{ fontSize: "1.5rem", flexShrink: 0 }}>
              {toastType === "danger" && "🚨"}
              {toastType === "warning" && "⚠️"}
              {toastType === "success" && "✅"}
              {toastType === "info" && "ℹ️"}
            </span>
            <div style={{ flex: 1 }}>
              <strong style={{ display: "block", marginBottom: "0.25rem" }}>
                {toastType === "danger" && "Occupancy Alert!"}
                {toastType === "warning" && "Warning"}
                {toastType === "success" && "Success"}
                {toastType === "info" && "Info"}
              </strong>
              <span style={{ fontSize: "0.9rem", opacity: 0.9 }}>
                {toastMessage}
              </span>
            </div>
            <button
              onClick={() => setShowToast(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "inherit",
                cursor: "pointer",
                fontSize: "1.25rem",
                padding: "0",
                opacity: 0.7,
                lineHeight: 1,
              }}
              onMouseEnter={(e) => (e.target.style.opacity = 1)}
              onMouseLeave={(e) => (e.target.style.opacity = 0.7)}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Slide-in animation */}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
      {/* TOP NAVIGATION BAR */}
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          backgroundColor: "var(--navbar-bg)",
          borderBottom: "1px solid var(--border-primary)",
          height: "65px",
        }}
      >
        <Nav mode={mode} setMode={setMode} />
      </div>

      {/* MAIN CONTAINER: LEFT MENU + CONTENT + RIGHT MENU */}
      <div
        style={{
          display: "flex",
          flex: 1,
          marginTop: "65px", // Account for fixed nav
          overflow: "hidden",
        }}
      >
        {/* LEFT SIDEBAR MENU */}
        <div
          style={{
            position: "fixed",
            left: 0,
            top: "65px",
            width: isMenuOpen ? "280px" : "50px",
            height: "calc(100vh - 65px)",
            backgroundColor: "var(--sidebar-bg)",
            borderRight: "1px solid var(--border-primary)",
            transition: "all 0.3s ease",
            zIndex: 999,
            overflow: "hidden",
          }}
        >
          {/* Toggle button - always visible */}
          {!isMenuOpen && (
            <button
              onClick={() => setIsMenuOpen(true)}
              style={{
                position: "absolute",
                right: "10px",
                top: "20px",
                width: "30px",
                height: "30px",
                background: "#667eea",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "16px",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "#5a67d8";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "#667eea";
              }}
              title="Open menu"
            >
              ☰
            </button>
          )}

          {/* Menu content - only show when open */}
          {isMenuOpen && (
            <div style={{ position: "relative", height: "100%" }}>
              <style>{`
                .menu-toggle-btn {
                  position: absolute !important;
                  left: 10px !important;
                  right: auto !important;
                  top: 10px !important;
                }
              `}</style>
              <Menu
                isOpen={isMenuOpen}
                onClose={() => setIsMenuOpen(false)}
                onToggle={() => setIsMenuOpen(!isMenuOpen)}
              />
            </div>
          )}
        </div>

        {/* MAIN CONTENT AREA */}
        <main
          style={{
            flex: 1,
            marginLeft: isMenuOpen ? "280px" : "50px",
            marginRight: isRightMenuOpen ? "320px" : "50px",
            padding: "2rem",
            overflowY: "auto",
            transition: "all 0.3s ease",
            backgroundColor: "var(--bg-primary)",
          }}
        >
          {/* PAGE HEADER */}
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
              📡 External Camera Control Center
            </h1>
            <p style={{ fontSize: "1rem", opacity: 0.9 }}>
              Full external camera functionality with manual layout control
            </p>
          </header>

          {/* Main Content */}
          <div style={{ padding: "0 2rem" }}>
            {/* Occupancy Widget */}
            <OccupancyWidget
              occupancyData={occupancyData}
              alertData={alertData}
              densityHeatmap={densityHeatmap}
              occupancyStatistics={occupancyStatistics}
              occupancyAlerts={occupancyAlerts}
              historicalDataAvailable={historicalDataAvailable}
              occupancyTimestamp={occupancyTimestamp}
            />

            {/* Camera URL Input & Controls */}
            <div
              style={{
                background: "var(--card-bg)",
                borderRadius: "12px",
                padding: "1.5rem",
                boxShadow: "var(--shadow-sm)",
                marginBottom: "2rem",
              }}
            >
              <h3
                style={{ margin: "0 0 1rem 0", color: "var(--text-primary)" }}
              >
                🎛️ Camera Settings
              </h3>

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
                    border: "1px solid var(--input-border)",
                    backgroundColor: "var(--input-bg)",
                    color: "var(--text-primary)",
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
                    color: "var(--text-primary)",
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
                    color: "var(--text-primary)",
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
                  background: isDarkMode ? "rgba(220, 53, 69, 0.2)" : "#fee2e2",
                  border: "2px solid var(--accent-danger)",
                  borderRadius: "8px",
                  color: "var(--accent-danger)",
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
                      background: "var(--card-bg)",
                      borderRadius: "12px",
                      padding: "1.5rem",
                      boxShadow: "var(--shadow-sm)",
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
                      background: isDarkMode
                        ? "rgba(251, 191, 36, 0.15)"
                        : "#fef3c7",
                      borderRadius: "12px",
                      border: "1px dashed var(--accent-warning)",
                      alignSelf: "start",
                      color: "var(--text-primary)",
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
                      background: "var(--card-bg)",
                      borderRadius: "12px",
                      padding: "1.5rem",
                      boxShadow: "var(--shadow-sm)",
                    }}
                  >
                    <h3
                      style={{
                        margin: "0 0 1rem 0",
                        color: "var(--text-primary)",
                      }}
                    >
                      🎨 Path Visualization
                    </h3>
                    <p
                      style={{
                        fontSize: "0.9rem",
                        color: "var(--text-secondary)",
                        margin: "0 0 0.75rem 0",
                      }}
                    >
                      Visualization is processed by the ML layer and includes:
                    </p>
                    <ul
                      style={{
                        margin: 0,
                        paddingLeft: "1.5rem",
                        color: "var(--text-secondary)",
                        fontSize: "0.9rem",
                      }}
                    >
                      <li>Real-time object detection and tracking</li>
                      <li>Path trajectory visualization with unique colors</li>
                      <li>Speed and direction analysis</li>
                      <li>Density heat mapping for crowd analysis</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>

        {/* MAIN RIGHT MENU (Occupancy Settings) */}
        <MainRightMenu isOpen={isRightMenuOpen} onToggle={setIsRightMenuOpen} />
      </div>
    </div>
  );
}

export default Main;
