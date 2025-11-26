import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import io from "socket.io-client";
import Chart from "chart.js/auto";
import "../../styles/OldMain.css";

function OldMain() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // State management
  const [isProcessing, setIsProcessing] = useState(false);
  const [videoSource, setVideoSource] = useState("webcam");
  const [ipAddress, setIpAddress] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [statusText, setStatusText] = useState("Ready");
  const [statusActive, setStatusActive] = useState(false);
  const [metrics, setMetrics] = useState({
    peopleCount: 0,
    uniqueCount: 0,
    crowdDensity: 0,
    avgSpeed: 0,
    fps: 0,
    processingTime: 0,
    csrnetCount: null,
  });

  const [metricsData, setMetricsData] = useState({
    maxPoints: 120,
    labels: [],
    peopleCount: [],
    crowdDensity: [],
  });

  const [analysisAssets, setAnalysisAssets] = useState({});
  const [trajectories, setTrajectories] = useState([]);

  // Refs
  const socketRef = useRef(null);
  const chartsRef = useRef({});
  const trajectoryCanvasRef = useRef(null);
  const trajectoryCtxRef = useRef(null);

  // Initialize Socket.IO
  useEffect(() => {
    socketRef.current = io();

    socketRef.current.on("connect", () => {
      console.log("Connected to server");
    });

    socketRef.current.on("metrics_update", (data) => {
      updateMetrics(data);
    });

    socketRef.current.on("analytics_update", (data) => {
      updateAnalytics(data);
    });

    socketRef.current.on("trajectories_update", (data) => {
      if (data.trajectories) {
        updateTrajectories(data.trajectories);
      }
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Initialize charts
  useEffect(() => {
    initializeCharts();
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access the dashboard</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  const initializeCharts = () => {
    // Destroy existing charts if they exist
    if (chartsRef.current.peopleCount) {
      chartsRef.current.peopleCount.destroy();
    }
    if (chartsRef.current.density) {
      chartsRef.current.density.destroy();
    }

    // People Count Chart
    const peopleCtx = document.getElementById("peopleCountChart");
    if (peopleCtx) {
      chartsRef.current.peopleCount = new Chart(peopleCtx, {
        type: "line",
        data: {
          labels: metricsData.labels,
          datasets: [
            {
              label: "People Count",
              data: metricsData.peopleCount,
              borderColor: "#667eea",
              backgroundColor: "rgba(102, 126, 234, 0.1)",
              fill: true,
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: true } },
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    }

    // Crowd Density Chart
    const densityCtx = document.getElementById("crowdDensityChart");
    if (densityCtx) {
      chartsRef.current.density = new Chart(densityCtx, {
        type: "line",
        data: {
          labels: metricsData.labels,
          datasets: [
            {
              label: "Crowd Density",
              data: metricsData.crowdDensity,
              borderColor: "#764ba2",
              backgroundColor: "rgba(118, 75, 162, 0.1)",
              fill: true,
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: true } },
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    }

    // Initialize Trajectory Canvas
    const canvas = trajectoryCanvasRef.current;
    if (canvas) {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      trajectoryCtxRef.current = canvas.getContext("2d");
    }
  };

  const updateMetrics = (data) => {
    setMetrics({
      peopleCount: data.current_count || 0,
      uniqueCount: data.unique_count || 0,
      crowdDensity: (data.crowd_density || 0).toFixed(2),
      avgSpeed: (data.average_speed || 0).toFixed(1),
      fps: (data.fps || 0).toFixed(1),
      processingTime: data.processing_time || 0,
      csrnetCount: data.csrnet_count,
    });

    addMetricPoint(
      new Date().toLocaleTimeString(),
      data.current_count || 0,
      data.crowd_density || 0
    );
  };

  const updateAnalytics = (data) => {
    console.log("Analytics update:", data);
  };

  const updateTrajectories = (trajData) => {
    setTrajectories(trajData);
    renderTrajectories(trajData);
  };

  const renderTrajectories = (trajData) => {
    const canvas = trajectoryCanvasRef.current;
    const ctx = trajectoryCtxRef.current;
    if (!ctx) return;

    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    trajData.forEach((traj) => {
      if (traj.points && traj.points.length > 0) {
        ctx.strokeStyle = `hsl(${(traj.id * 137.5) % 360}, 100%, 50%)`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(traj.points[0][0], traj.points[0][1]);
        for (let i = 1; i < traj.points.length; i++) {
          ctx.lineTo(traj.points[i][0], traj.points[i][1]);
        }
        ctx.stroke();
      }
    });
  };

  const addMetricPoint = (label, count, density) => {
    setMetricsData((prev) => {
      const newData = { ...prev };
      if (newData.labels.length >= prev.maxPoints) {
        newData.labels.shift();
        newData.peopleCount.shift();
        newData.crowdDensity.shift();
      }
      newData.labels.push(label);
      newData.peopleCount.push(count);
      newData.crowdDensity.push(density);
      return newData;
    });

    updateCharts();
  };

  const updateCharts = () => {
    if (chartsRef.current.peopleCount) {
      chartsRef.current.peopleCount.data.labels = metricsData.labels;
      chartsRef.current.peopleCount.data.datasets[0].data =
        metricsData.peopleCount;
      chartsRef.current.peopleCount.update();
    }

    if (chartsRef.current.density) {
      chartsRef.current.density.data.labels = metricsData.labels;
      chartsRef.current.density.data.datasets[0].data =
        metricsData.crowdDensity;
      chartsRef.current.density.update();
    }
  };

  const testConnection = async () => {
    if (!ipAddress) {
      alert("Please enter an IP address");
      return;
    }

    const testBtn = document.getElementById("testConnection");
    testBtn.disabled = true;
    testBtn.textContent = "Testing...";

    try {
      const response = await fetch("/api/test-connection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: ipAddress }),
      });

      const data = await response.json();
      if (data.success) {
        alert("Connection successful!");
      } else {
        alert("Connection failed: " + data.error);
      }
    } catch (error) {
      alert("Connection test failed: " + error.message);
    } finally {
      testBtn.disabled = false;
      testBtn.textContent = "Test Connection";
    }
  };

  const analyzeImage = async () => {
    if (!imageFile) {
      alert("Please select an image");
      return;
    }

    const analyzeBtn = document.getElementById("analyzeImageBtn");
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    const formData = new FormData();
    formData.append("file", imageFile);

    try {
      const response = await fetch("/api/analyze-image", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (response.ok) {
        setMetrics({
          ...metrics,
          peopleCount: result.current_count || 0,
          uniqueCount: result.unique_count || 0,
          crowdDensity: (result.crowd_density || 0).toFixed(2),
          avgSpeed: (result.average_speed || 0).toFixed(1),
          processingTime: result.processing_time || 0,
          csrnetCount: result.csrnet_count,
        });

        if (result.heatmap_image) {
          setAnalysisAssets((prev) => ({
            ...prev,
            heatmap: result.heatmap_image,
          }));
        }
      } else {
        alert("Error analyzing image: " + result.error);
      }
    } catch (error) {
      alert("Error analyzing image: " + error.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze Image";
    }
  };

  const startAnalysis = async () => {
    if (videoSource === "image") {
      alert("Please use the Image Analysis section for images");
      return;
    }

    let source;
    switch (videoSource) {
      case "webcam":
        source = "webcam";
        break;
      case "ip_webcam":
        source = ipAddress;
        break;
      case "video_file":
        source = videoFile ? videoFile.name : null;
        break;
      default:
        source = null;
    }

    if (!source) {
      alert("Please configure the video source");
      return;
    }

    try {
      setIsProcessing(true);
      setStatusText("Starting analysis...");
      setStatusActive(true);

      const response = await fetch("/api/start-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });

      if (response.ok) {
        setStatusText("Analysis running");
      } else {
        alert("Failed to start analysis");
        setIsProcessing(false);
        setStatusActive(false);
      }
    } catch (error) {
      alert("Error: " + error.message);
      setIsProcessing(false);
      setStatusActive(false);
    }
  };

  const stopAnalysis = async () => {
    try {
      const response = await fetch("/api/stop-analysis", { method: "POST" });
      if (response.ok) {
        setIsProcessing(false);
        setStatusText("Analysis stopped");
        setStatusActive(false);
      }
    } catch (error) {
      alert("Error stopping analysis: " + error.message);
    }
  };

  const exportData = async () => {
    try {
      const response = await fetch("/api/export-metrics");
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "metrics.json";
        a.click();
      }
    } catch (error) {
      alert("Error exporting data: " + error.message);
    }
  };

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="mb-2">📊 Crowd Analysis Dashboard</h1>
          <p className="text-muted">
            Real-time crowd detection, tracking, and density analytics
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="row">
        <div className="col-12">
          <div className="control-panel">
            <div className="row g-3">
              {/* Video Source Selection */}
              <div className="col-md-3">
                <label className="form-label">Video Source</label>
                <select
                  className="form-select"
                  value={videoSource}
                  onChange={(e) => setVideoSource(e.target.value)}
                  disabled={isProcessing}
                >
                  <option value="webcam">Webcam</option>
                  <option value="ip_webcam">IP Camera</option>
                  <option value="video_file">Video File</option>
                  <option value="image">Image Analysis</option>
                </select>
              </div>

              {/* IP Address Input */}
              {videoSource === "ip_webcam" && (
                <>
                  <div className="col-md-3">
                    <label className="form-label">Camera IP</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g., http://192.168.1.100:8080/video"
                      value={ipAddress}
                      onChange={(e) => setIpAddress(e.target.value)}
                      disabled={isProcessing}
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">&nbsp;</label>
                    <button
                      className="btn btn-info w-100"
                      onClick={testConnection}
                      disabled={isProcessing}
                    >
                      Test Connection
                    </button>
                  </div>
                </>
              )}

              {/* Video File Input */}
              {videoSource === "video_file" && (
                <div className="col-md-3">
                  <label className="form-label">Upload Video</label>
                  <input
                    type="file"
                    className="form-control"
                    accept="video/*"
                    onChange={(e) => setVideoFile(e.target.files[0])}
                    disabled={isProcessing}
                  />
                </div>
              )}

              {/* Image File Input */}
              {videoSource === "image" && (
                <>
                  <div className="col-md-3">
                    <label className="form-label">Upload Image</label>
                    <input
                      type="file"
                      className="form-control"
                      accept="image/*"
                      onChange={(e) => setImageFile(e.target.files[0])}
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">&nbsp;</label>
                    <button
                      className="btn btn-primary w-100"
                      id="analyzeImageBtn"
                      onClick={analyzeImage}
                    >
                      Analyze Image
                    </button>
                  </div>
                </>
              )}

              {/* Control Buttons */}
              <div className="col-md-2">
                <label className="form-label">&nbsp;</label>
                <div className="d-grid gap-2">
                  <button
                    className="btn btn-success"
                    id="startBtn"
                    onClick={startAnalysis}
                    disabled={isProcessing || videoSource === "image"}
                  >
                    Start
                  </button>
                </div>
              </div>

              <div className="col-md-2">
                <label className="form-label">&nbsp;</label>
                <div className="d-grid gap-2">
                  <button
                    className="btn btn-danger"
                    id="stopBtn"
                    onClick={stopAnalysis}
                    disabled={!isProcessing}
                  >
                    Stop
                  </button>
                </div>
              </div>

              <div className="col-md-2">
                <label className="form-label">&nbsp;</label>
                <div className="d-grid gap-2">
                  <button
                    className="btn btn-secondary"
                    id="exportBtn"
                    onClick={exportData}
                  >
                    Export
                  </button>
                </div>
              </div>
            </div>

            {/* Status Bar */}
            <div className="row mt-3">
              <div className="col-12">
                <small>
                  <span
                    className={`status-indicator ${
                      statusActive ? "status-active" : "status-inactive"
                    }`}
                  ></span>
                  <span id="statusText">{statusText}</span>
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="row g-4">
        {/* Video Feeds */}
        <div className="col-lg-8">
          <div className="video-container">
            <img
              id="videoFeed"
              src={isProcessing ? `/video_feed?t=${Date.now()}` : ""}
              alt="Live Feed"
              className="video-feed"
            />
          </div>
          <small className="text-muted d-block mt-2">
            Processed video feed with detections
          </small>
        </div>

        {/* Metrics Panel */}
        <div className="col-lg-4">
          <div className="row g-3">
            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">People Count</p>
                  <p className="metric-value" id="peopleCount">
                    {metrics.peopleCount}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">Unique IDs</p>
                  <p className="metric-value" id="uniqueCount">
                    {metrics.uniqueCount}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">Crowd Density</p>
                  <p className="metric-value" id="crowdDensity">
                    {metrics.crowdDensity}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">Avg Speed</p>
                  <p className="metric-value" id="avgSpeed">
                    {metrics.avgSpeed}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">FPS</p>
                  <p className="metric-value" id="currentFps">
                    {metrics.fps}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="metric-card">
                <div className="card-body">
                  <p className="metric-label">Processing Time</p>
                  <p className="metric-value" id="processingTime">
                    {metrics.processingTime}ms
                  </p>
                </div>
              </div>
            </div>

            {metrics.csrnetCount !== null && (
              <div className="col-12">
                <div className="metric-card">
                  <div className="card-body">
                    <p className="metric-label">CSRNet Count</p>
                    <p className="metric-value" id="csrnetCount">
                      {metrics.csrnetCount}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="row justify-content-center g-4 mt-4">
        <div className="col-12 col-lg-8 col-xl-6">
          <div className="chart-container">
            <canvas id="peopleCountChart"></canvas>
          </div>
        </div>
        <div className="col-12 col-lg-8 col-xl-6">
          <div className="chart-container">
            <canvas id="crowdDensityChart"></canvas>
          </div>
        </div>
      </div>

      {/* Trajectory Visualization */}
      <div className="row justify-content-center g-4 mt-4">
        <div className="col-12 col-lg-8 col-xl-6">
          <div className="chart-container">
            <canvas
              ref={trajectoryCanvasRef}
              className="trajectory-canvas"
            ></canvas>
          </div>
          <small className="text-muted d-block mt-2">
            Trajectory visualization
          </small>
        </div>
      </div>

      {/* Analysis Assets */}
      {Object.keys(analysisAssets).length > 0 && (
        <div className="row mt-4">
          <div className="col-12">
            <h5>Analysis Results</h5>
            <div className="row g-3">
              {Object.entries(analysisAssets).map(([key, value]) => (
                <div className="col-md-6" key={key}>
                  <div className="card">
                    <img src={value} className="card-img-top" alt={key} />
                    <div className="card-body">
                      <p className="card-text text-capitalize">{key}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OldMain;
