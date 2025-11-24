import React, { useState, useRef } from "react";
import "../../../styles/YOLOUploader.css";
import TrajectoryCanvas from "../../Trajectory/TrajectoryCanvas";
import HeatmapOverlay from "../../Heatmap/HeatmapOverlay";
import CountDisplay from "../../CountDisplay";
import BackendStatus from "../../BackendStatus";

function YOLOUploader() {
  const [selectedModel, setSelectedModel] = useState("yolov8n");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // New feature flags
  const [enableTracking, setEnableTracking] = useState(false);
  const [enableHeatmap, setEnableHeatmap] = useState(true);

  const fileInputRef = useRef(null);
  const imgRef = useRef(null);

  // Available YOLO models
  const yoloModels = [
    {
      id: "yolov8n",
      name: "YOLOv8 Nano",
      description: "Fastest & lightest (1.9M parameters)",
      specs: "5.3M params | ~4ms inference",
      recommended: "Real-time, low resource",
    },
    {
      id: "yolov8s",
      name: "YOLOv8 Small",
      description: "Small model for better accuracy (11.2M)",
      specs: "11.2M params | ~6ms inference",
      recommended: "Balanced speed/accuracy",
    },
    {
      id: "yolov8m",
      name: "YOLOv8 Medium",
      description: "Medium model (25.9M parameters)",
      specs: "25.9M params | ~11ms inference",
      recommended: "High accuracy needed",
    },
    {
      id: "yolov8l",
      name: "YOLOv8 Large",
      description: "Large model for best accuracy (43.7M)",
      specs: "43.7M params | ~20ms inference",
      recommended: "Maximum accuracy required",
    },
    {
      id: "yolov8x",
      name: "YOLOv8 XLarge",
      description: "Largest model (68.2M parameters)",
      specs: "68.2M params | ~30ms inference",
      recommended: "Best accuracy, GPU required",
    },
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("model", selectedModel);
      formData.append("confidence", confidenceThreshold);
      formData.append("enable_tracking", enableTracking);
      formData.append("enable_heatmap", enableHeatmap);

      console.log("📤 Sending request to backend...");
      console.log(
        "File:",
        selectedFile.name,
        selectedFile.type,
        selectedFile.size,
        "bytes"
      );
      console.log("Model:", selectedModel);
      console.log("URL:", "http://localhost:8000/api/v1/yolo/detect");

      // Call the detect endpoint for detailed results
      const response = await fetch("http://localhost:8000/api/v1/yolo/detect", {
        method: "POST",
        body: formData,
        // Note: Don't set Content-Type header - browser will set it with boundary for FormData
      });

      console.log(
        "📥 Response received:",
        response.status,
        response.statusText
      );

      if (!response.ok) {
        let errorMessage = "Prediction failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("✅ Prediction successful:", data);
      setResult(data);
    } catch (err) {
      console.error("❌ Prediction error:", err);

      // Provide more specific error messages
      let errorMessage = err.message;
      if (err.message === "Failed to fetch") {
        errorMessage =
          "Cannot connect to backend server. Please ensure:\n" +
          "1. Backend is running (python run.py in backend folder)\n" +
          "2. Backend is accessible at http://localhost:8000\n" +
          "3. CORS is properly configured\n" +
          "4. No firewall blocking the connection";
      }

      setError(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="yolo-uploader">
      <div className="yolo-header">
        <h2>🚀 YOLOv8 Object Detection</h2>
        <p>Real-time crowd counting with advanced detection</p>
      </div>

      <div className="yolo-container">
        {/* Left Column: Model Selection & Configuration */}
        <div className="yolo-config-panel">
          <section className="model-selection">
            <h3>📊 Select Detection Model</h3>
            <p className="section-subtitle">
              Choose a model based on your speed/accuracy needs
            </p>

            <div className="model-grid">
              {yoloModels.map((model) => (
                <div
                  key={model.id}
                  className={`model-card ${
                    selectedModel === model.id ? "selected" : ""
                  }`}
                  onClick={() => setSelectedModel(model.id)}
                >
                  <div className="model-card-header">
                    <h4>{model.name}</h4>
                    <span className="model-badge">{model.specs}</span>
                  </div>
                  <p className="model-description">{model.description}</p>
                  <div className="model-recommended">
                    <span className="recommended-label">
                      💡 {model.recommended}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Confidence Threshold */}
          <section className="confidence-section">
            <h3>🎯 Detection Threshold</h3>
            <div className="slider-container">
              <label>
                Confidence Level:{" "}
                <strong>{confidenceThreshold.toFixed(2)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) =>
                  setConfidenceThreshold(parseFloat(e.target.value))
                }
                className="threshold-slider"
              />
              <div className="slider-labels">
                <span>Low (0.0)</span>
                <span>Medium (0.5)</span>
                <span>High (1.0)</span>
              </div>
              <p className="slider-hint">
                ⓘ Higher values = more confident detections, fewer false
                positives
              </p>
            </div>
          </section>

          {/* Feature Toggles */}
          <section className="feature-toggles-section">
            <h3>⚙️ Advanced Features</h3>
            <div className="toggle-group">
              <div className="toggle-item">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={enableTracking}
                    onChange={(e) => setEnableTracking(e.target.checked)}
                    className="toggle-checkbox"
                  />
                  <span className="toggle-text">
                    🎯 Enable Trajectory Tracking
                  </span>
                </label>
                <p className="toggle-hint">
                  Shows object paths and track IDs (for video/sequence
                  processing)
                </p>
              </div>

              <div className="toggle-item">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={enableHeatmap}
                    onChange={(e) => setEnableHeatmap(e.target.checked)}
                    className="toggle-checkbox"
                  />
                  <span className="toggle-text">🔥 Show Detection Overlay</span>
                </label>
                <p className="toggle-hint">
                  Displays annotated image with bounding boxes
                </p>
              </div>
            </div>
          </section>

          {/* Model Comparison */}
          <section className="comparison-section">
            <h3>📈 Model Comparison</h3>
            <div className="comparison-table">
              <div className="comparison-row header">
                <div className="col">Model</div>
                <div className="col">Speed</div>
                <div className="col">Accuracy</div>
                <div className="col">Memory</div>
              </div>
              {yoloModels.map((model) => (
                <div key={model.id} className="comparison-row">
                  <div className="col">{model.name}</div>
                  <div className="col">
                    {model.id === "yolov8n" && "⚡⚡⚡"}
                    {model.id === "yolov8s" && "⚡⚡⚡"}
                    {model.id === "yolov8m" && "⚡⚡"}
                    {model.id === "yolov8l" && "⚡"}
                    {model.id === "yolov8x" && "🐢"}
                  </div>
                  <div className="col">
                    {model.id === "yolov8n" && "★★★"}
                    {model.id === "yolov8s" && "★★★★"}
                    {model.id === "yolov8m" && "★★★★"}
                    {model.id === "yolov8l" && "★★★★★"}
                    {model.id === "yolov8x" && "★★★★★"}
                  </div>
                  <div className="col">
                    {model.id === "yolov8n" && "300MB"}
                    {model.id === "yolov8s" && "650MB"}
                    {model.id === "yolov8m" && "1.4GB"}
                    {model.id === "yolov8l" && "2.5GB"}
                    {model.id === "yolov8x" && "3.8GB"}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column: Image Upload & Results */}
        <div className="yolo-content-panel">
          {/* Image Upload Area */}
          <section className="upload-section">
            <h3>📤 Upload Image</h3>

            {!preview ? (
              <div className="upload-box" onClick={handleUploadClick}>
                <div className="upload-icon">📸</div>
                <h4>Click to upload image</h4>
                <p>or drag and drop</p>
                <p className="upload-hint">PNG, JPG, GIF up to 10MB</p>
              </div>
            ) : (
              <div className="preview-container">
                <img src={preview} alt="Preview" className="preview-image" />
                <div className="preview-info">
                  <p>✅ {selectedFile.name}</p>
                  <p className="file-size">
                    ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                </div>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />
          </section>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              onClick={handleUploadClick}
              className="btn btn-secondary"
              disabled={loading}
            >
              📎 {preview ? "Change Image" : "Select Image"}
            </button>
            <button
              onClick={handlePredict}
              className="btn btn-primary"
              disabled={!selectedFile || loading}
            >
              {loading ? "🔄 Processing..." : "🚀 Run Detection"}
            </button>
            {(preview || result) && (
              <button
                onClick={handleClear}
                className="btn btn-outline"
                disabled={loading}
              >
                🗑️ Clear
              </button>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <div style={{ whiteSpace: "pre-wrap", flex: 1 }}>{error}</div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <section className="results-section">
              <h3>📊 Detection Results</h3>

              {/* Annotated Image with Overlays */}
              <div
                className="annotated-image-container"
                style={{ position: "relative" }}
              >
                {result.annotated_image && (
                  <img
                    ref={imgRef}
                    src={result.annotated_image}
                    alt="Annotated Result"
                    className="annotated-image"
                  />
                )}

                {/* Trajectory overlay using TrajectoryCanvas component */}
                {enableTracking && result.tracks && (
                  <TrajectoryCanvas
                    sourceRef={imgRef}
                    results={result}
                    enableTracking={enableTracking}
                  />
                )}
              </div>

              {/* Count Display using CountDisplay component */}
              <CountDisplay
                results={result}
                enableTracking={enableTracking}
                displayMode="stats"
              />

              <div className="results-grid">
                <div className="result-card">
                  <div className="result-label"> Detection Count</div>
                  <div className="result-value">{result.num_boxes}</div>
                  <div className="result-hint">Bounding boxes detected</div>
                </div>

                <div className="result-card">
                  <div className="result-label">🎯 Avg Confidence</div>
                  <div className="result-value">
                    {(result.average_confidence * 100).toFixed(1)}%
                  </div>
                  <div className="result-hint">
                    Range: {(result.min_confidence * 100).toFixed(1)}% -{" "}
                    {(result.max_confidence * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="result-card">
                  <div className="result-label">⚡ Inference Time</div>
                  <div className="result-value">
                    {result.inference_time_ms.toFixed(1)}ms
                  </div>
                  <div className="result-hint">
                    {(1000 / result.inference_time_ms).toFixed(1)} FPS
                  </div>
                </div>
              </div>

              {/* Detailed Boxes Table */}
              {result.boxes && result.boxes.length > 0 && (
                <div className="boxes-section">
                  <h4>🔍 Detected Objects (Top 10)</h4>
                  <div className="boxes-table">
                    <div className="table-header">
                      <div className="col-id">ID</div>
                      <div className="col-coords">Coordinates</div>
                      <div className="col-size">Size</div>
                      <div className="col-conf">Confidence</div>
                    </div>
                    {result.boxes.slice(0, 10).map((box, idx) => (
                      <div key={idx} className="table-row">
                        <div className="col-id">{idx + 1}</div>
                        <div className="col-coords">
                          ({box.x1}, {box.y1}) → ({box.x2}, {box.y2})
                        </div>
                        <div className="col-size">
                          {(box.x2 - box.x1).toFixed(0)}×
                          {(box.y2 - box.y1).toFixed(0)}
                        </div>
                        <div className="col-conf">
                          <span className="confidence-badge">
                            {(box.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  {result.boxes.length > 10 && (
                    <p className="more-boxes">
                      + {result.boxes.length - 10} more detections
                    </p>
                  )}
                </div>
              )}

              {/* Model & Device Info */}
              <div className="info-section">
                <div className="info-item">
                  <span className="info-label">Model:</span>
                  <span className="info-value">{result.model}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Device:</span>
                  <span className="info-value">{result.device}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Approach:</span>
                  <span className="info-value">{result.approach}</span>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>

      {/* Backend Connection Status Indicator */}
      <BackendStatus />
    </div>
  );
}

export default YOLOUploader;
