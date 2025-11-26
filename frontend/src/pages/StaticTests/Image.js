import React, { useState, useRef, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/WebcamPage.css";
import "../../styles/WebcamCounterNew.css";
import { useAuth } from "../../context/AuthContext";
import CSRNetUploader from "../../components/Models/CSRNet/CSRNetUploader";
import VMambaUploader from "../../components/Models/TMTB/VMambaUploader";
import MCNNUploader from "../../components/Models/MCNN/MCNNUploader";
import YOLOUploader from "../../components/Models/YOLO/YOLOUploader";

function Image() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Model selection state
  const modelOptions = useMemo(
    () => [
      {
        id: "CSRNet",
        label: "CSRNet",
        description: "Density-map baseline trained for ShanghaiTech",
        ready: true,
        badge: "Production",
      },
      {
        id: "VMamba",
        label: "VMamba TMTB",
        description: "Fine-tuned best checkpoint on ShanghaiTech Part A",
        ready: true,
        badge: "Best Accuracy",
      },
      {
        id: "MCNN",
        label: "MCNN",
        description: "Legacy multi-column CNN (coming soon)",
        ready: false,
        badge: "Roadmap",
      },
      {
        id: "YOLOv8",
        label: "YOLOv8",
        description:
          "Real-time object detection for crowd counting with tracking",
        ready: true,
        badge: "Production",
      },
    ],
    []
  );

  const [selectedModel, setSelectedModel] = useState(
    modelOptions.find((option) => option.ready)?.id || "CSRNet"
  );

  const [showModelSelector, setShowModelSelector] = useState(true);

  const activeModel = useMemo(
    () => modelOptions.find((option) => option.id === selectedModel),
    [modelOptions, selectedModel]
  );

  // State Management
  const [isStreaming, setIsStreaming] = useState(false);
  const [results, setResults] = useState(null);
  const [fps, setFps] = useState(0);
  const [countHistory, setCountHistory] = useState([]);
  const [heatmapImage, setHeatmapImage] = useState(null);
  const [enableTracking, setEnableTracking] = useState(false);
  const [enableHeatmap, setEnableHeatmap] = useState(false);
  const [detectionThreshold, setDetectionThreshold] = useState(0.5);
  const [showLiveCount, setShowLiveCount] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showMetrics, setShowMetrics] = useState(true);
  const [showGraph, setShowGraph] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const [uniqueCount, setUniqueCount] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [currentAutoModel, setCurrentAutoModel] = useState("csrnet");
  const [autoSwitch, setAutoSwitch] = useState(false);
  const [autoSwitchThreshold, setAutoSwitchThreshold] = useState(50);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  // Handle file selection
  const handleFileSelect = useCallback((event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }

    setSelectedFile(file);
    setError(null);
    setResults(null);
    setCountHistory([]);
    setHeatmapImage(null);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  }, []);

  // Handle drag and drop
  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      const file = event.dataTransfer.files?.[0];
      if (file) {
        const fakeEvent = {
          target: { files: [file] },
        };
        handleFileSelect(fakeEvent);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
  }, []);

  // Process image
  const handleProcessImage = useCallback(async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setIsStreaming(true);
    setError(null);

    try {
      // Convert image to base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const base64Data = e.target.result.split(",")[1];

          // Send to backend
          const response = await fetch(
            "http://localhost:8000/api/v1/predict/image",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                image: base64Data,
                model: selectedModel.toLowerCase(),
                detect_threshold: detectionThreshold,
                tracking: enableTracking,
                heatmap: enableHeatmap,
              }),
            }
          );

          if (!response.ok) {
            throw new Error("Failed to process image");
          }

          const data = await response.json();
          if (data.success) {
            setResults(data);
            setFps(1000 / data.inference_time_ms);
            setFrameCount((prev) => prev + 1);

            // Update count history
            setCountHistory((prev) => {
              const newHistory = [
                ...prev,
                { time: Date.now(), count: data.count || 0 },
              ];
              return newHistory.slice(-30);
            });

            // Update heatmap
            if (enableHeatmap && data.heatmap) {
              setHeatmapImage(data.heatmap);
            }

            // Update unique count if tracking
            if (enableTracking && data.unique_count !== undefined) {
              setUniqueCount(data.unique_count);
            }
          } else {
            setError(data.error || "Processing failed");
          }
        } catch (err) {
          setError(err.message || "Error processing image");
        } finally {
          setIsStreaming(false);
        }
      };

      reader.readAsDataURL(selectedFile);
    } catch (err) {
      setError(err.message || "Error processing image");
      setIsStreaming(false);
    }
  }, [
    selectedFile,
    selectedModel,
    detectionThreshold,
    enableTracking,
    enableHeatmap,
  ]);

  const handleClearImage = useCallback(() => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResults(null);
    setHeatmapImage(null);
    setCountHistory([]);
    setError(null);
    setFrameCount(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="webcam-page">
        <p>Please log in to access the image upload</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", width: "100%" }}>
      <main
        className="webcam-main"
        style={{ flex: 1, width: "100%", margin: "0", padding: "2rem 1rem" }}
      >
        {/* Model Selection Section */}
        {showModelSelector && (
          <section
            className="model-toggle-section"
            style={{ marginBottom: "2rem" }}
          >
            <h2 className="model-toggle-title">Choose Your Inference Model</h2>
            <p className="model-toggle-subtitle">
              Switch between production-ready CSRNet and fine-tuned VMamba-TMTB.
              Select the model that best fits your needs.
            </p>
            <div className="model-toggle-grid">
              {modelOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  className={`model-chip ${
                    selectedModel === option.id ? "active" : ""
                  } ${option.ready ? "" : "disabled"}`}
                  onClick={() => option.ready && setSelectedModel(option.id)}
                  disabled={!option.ready}
                  style={{
                    border:
                      selectedModel === option.id
                        ? "2px solid #667eea"
                        : "2px solid rgba(102, 126, 234, 0.25)",
                    background:
                      selectedModel === option.id
                        ? "rgba(102, 126, 234, 0.1)"
                        : "white",
                    borderRadius: "12px",
                    padding: "1rem",
                    cursor: option.ready ? "pointer" : "not-allowed",
                    opacity: option.ready ? 1 : 0.6,
                    transition: "all 0.2s",
                  }}
                >
                  <strong>{option.label}</strong>
                  <p
                    style={{
                      margin: "0.5rem 0 0 0",
                      fontSize: "0.9rem",
                      color: "#666",
                    }}
                  >
                    {option.description}
                  </p>
                  {option.badge && (
                    <span
                      style={{
                        display: "inline-block",
                        marginTop: "0.5rem",
                        padding: "0.25rem 0.75rem",
                        background: option.ready ? "#667eea" : "#ccc",
                        color: "white",
                        borderRadius: "20px",
                        fontSize: "0.75rem",
                        fontWeight: "600",
                      }}
                    >
                      {option.badge}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Model-Specific Uploader */}
        {activeModel && (
          <section style={{ marginBottom: "2rem" }}>
            {activeModel.id === "CSRNet" && <CSRNetUploader />}
            {activeModel.id === "VMamba" && <VMambaUploader />}
            {activeModel.id === "YOLOv8" && <YOLOUploader />}
            {activeModel.id === "MCNN" && <MCNNUploader />}
          </section>
        )}

        {/* Divider */}
        {showModelSelector && (
          <hr
            style={{
              margin: "3rem 0",
              border: "none",
              borderTop: "1px solid #eee",
            }}
          />
        )}

        {/* Main Layout with Sidebar */}
        {!showModelSelector && (
          <div className="webcam-counter-grid">
            {/* Settings Sidebar */}
            {/* TODO: Visualization components deleted - needs refactoring */}
            {/*
            <SettingsSidebar
              isStreaming={isStreaming}
              error={error}
              selectedModel={selectedModel}
              setSelectedModel={setSelectedModel}
              enableTracking={enableTracking}
              setEnableTracking={setEnableTracking}
              enableHeatmap={enableHeatmap}
              setEnableHeatmap={setEnableHeatmap}
              detectionThreshold={detectionThreshold}
              setDetectionThreshold={setDetectionThreshold}
              showLiveCount={showLiveCount}
              setShowLiveCount={setShowLiveCount}
              showHeatmap={showHeatmap}
              setShowHeatmap={setShowHeatmap}
              showMetrics={showMetrics}
              setShowMetrics={setShowMetrics}
              showGraph={showGraph}
              setShowGraph={setShowGraph}
              onStart={handleProcessImage}
              onStop={handleClearImage}
              fps={fps}
              frameCount={frameCount}
              sourceType="image"
            />
            */}

            {/* Visualization Grid - Modular Cards */}
            <section className="visualization-grid">
              <p
                style={{ padding: "2rem", textAlign: "center", color: "#999" }}
              >
                Image upload functionality available above. Visualization cards
                temporarily disabled.
              </p>
              {/* Heatmap Card - Commented out (component deleted) */}
              {/*
              {showHeatmap && (
                <HeatmapCard
                  isStreaming={results !== null}
                  enableHeatmap={enableHeatmap}
                  heatmapImage={heatmapImage}
                  modelType={selectedModel}
                  displayMode="card"
                />
              )}
              */}

              {/* Metrics Card - Commented out (component deleted) */}
              {/*
              {showMetrics && (
                <MetricsCard
                  isStreaming={results !== null}
                  enableTracking={enableTracking}
                  results={results}
                />
              )}
              */}

              {/* Graph Card - Commented out (component deleted) */}
              {/*
              {showGraph && (
                <GraphCard
                  isStreaming={results !== null}
                  countHistory={countHistory}
                  title="Image Analysis History"
                />
              )}
              */}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default Image;
