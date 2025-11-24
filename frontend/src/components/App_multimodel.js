import React, { useState, useRef, useEffect } from "react";
import "../styles/App_multimodel.css";
import Webcam from "../pages/webcam/Webcam";

function App() {
  const [mode, setMode] = useState("upload"); // "upload" or "webcam"
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);
  const [currentModel, setCurrentModel] = useState("vmamba_tmtb");
  const [modelLoading, setModelLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Fetch available models on component mount
  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/models");
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models);
        setCurrentModel(data.current_model);
      }
    } catch (err) {
      console.error("Failed to fetch models:", err);
    }
  };

  // Handle model selection
  const handleModelChange = async (modelType) => {
    if (modelType === currentModel) return;

    setModelLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/select-model", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model_type: modelType,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentModel(data.current_model);
        // Clear previous results when switching models
        setResults(null);
      } else {
        throw new Error("Failed to switch model");
      }
    } catch (err) {
      setError(`Failed to switch model: ${err.message}`);
    } finally {
      setModelLoading(false);
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
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

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  // Handle drag and drop
  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      // Simulate file input change
      const fakeEvent = {
        target: { files: [file] },
      };
      handleFileSelect(fakeEvent);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  // Submit image for counting
  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/count", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Failed to process image: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset everything
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎥 Crowd Flow Prediction Analyzer</h1>
        <p className="subtitle">Multi-Model AI-Powered Crowd Counting System</p>
      </header>

      {/* Model Selection Section */}
      <div className="model-selector-container">
        <div className="model-selector">
          <h3>🤖 Select Model Architecture</h3>
          <div className="model-buttons">
            {Object.entries(availableModels).map(([modelId, modelInfo]) => (
              <button
                key={modelId}
                className={`model-button ${
                  currentModel === modelId ? "active" : ""
                } ${!modelInfo.checkpoint_exists ? "disabled" : ""}`}
                onClick={() => handleModelChange(modelId)}
                disabled={modelLoading || !modelInfo.checkpoint_exists}
                title={
                  !modelInfo.checkpoint_exists
                    ? "Checkpoint not available"
                    : modelInfo.description
                }
              >
                <span className="model-name">{modelInfo.name}</span>
                {!modelInfo.checkpoint_exists && (
                  <span className="badge">Not Available</span>
                )}
                {currentModel === modelId && (
                  <span className="badge active-badge">Active</span>
                )}
              </button>
            ))}
          </div>
          {modelLoading && (
            <div className="model-loading">
              <div className="spinner"></div>
              <span>Loading model...</span>
            </div>
          )}
          {currentModel && availableModels[currentModel] && (
            <div className="model-info">
              <p>
                <strong>Current Model:</strong>{" "}
                {availableModels[currentModel].name}
              </p>
              <p className="model-description">
                {availableModels[currentModel].description}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Mode Selection */}
      <div className="mode-selector">
        <button
          className={`mode-button ${mode === "upload" ? "active" : ""}`}
          onClick={() => setMode("upload")}
        >
          📤 Upload Image
        </button>
        <button
          className={`mode-button ${mode === "webcam" ? "active" : ""}`}
          onClick={() => setMode("webcam")}
        >
          📹 Live Webcam
        </button>
      </div>

      <main className="App-main">
        {mode === "webcam" ? (
          <Webcam currentModel={currentModel} />
        ) : (
          <div className="upload-container">
            {/* Upload Area */}
            <div
              className="upload-area"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              {previewUrl ? (
                <div className="preview-container">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="preview-image"
                  />
                  <div className="preview-overlay">
                    <p>Click to change image</p>
                  </div>
                </div>
              ) : (
                <div className="upload-prompt">
                  <div className="upload-icon">📁</div>
                  <p>Drag & Drop an image here</p>
                  <p className="upload-subtitle">or click to browse</p>
                  <p className="upload-hint">Supports: JPG, PNG (max 10MB)</p>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />

            {/* Action Buttons */}
            <div className="button-group">
              <button
                className="primary-button"
                onClick={handleSubmit}
                disabled={!selectedFile || loading}
              >
                {loading ? "Processing..." : "🔍 Count Crowd"}
              </button>
              {selectedFile && (
                <button className="secondary-button" onClick={handleReset}>
                  🔄 Reset
                </button>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}

            {/* Results Display */}
            {results && (
              <div className="results-container">
                <h2>Results</h2>

                {/* Count Display */}
                <div className="count-display">
                  <div className="count-value">{results.count}</div>
                  <div className="count-label">Estimated People</div>
                </div>

                {/* Reasoning */}
                {results.reasoning && (
                  <div className="reasoning-box">
                    <h3>Analysis</h3>
                    <p>{results.reasoning}</p>
                  </div>
                )}

                {/* Performance Metrics */}
                {results.timing && (
                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="metric-value">
                        {results.timing.total_ms}ms
                      </div>
                      <div className="metric-label">Processing Time</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-value">
                        {results.timing.inference_ms}ms
                      </div>
                      <div className="metric-label">Inference Time</div>
                    </div>
                    {results.image_size && (
                      <div className="metric-card">
                        <div className="metric-value">{results.image_size}</div>
                        <div className="metric-label">Image Size</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Density Map Stats */}
                {results.density_map_stats && (
                  <div className="density-stats">
                    <h3>Density Map Statistics</h3>
                    <div className="stats-grid">
                      <div className="stat-item">
                        <span className="stat-label">Sum:</span>
                        <span className="stat-value">
                          {results.density_map_stats.sum.toFixed(2)}
                        </span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Mean:</span>
                        <span className="stat-value">
                          {results.density_map_stats.mean.toFixed(4)}
                        </span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Max:</span>
                        <span className="stat-value">
                          {results.density_map_stats.max.toFixed(4)}
                        </span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Min:</span>
                        <span className="stat-value">
                          {results.density_map_stats.min.toFixed(4)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>
          Powered by{" "}
          {currentModel && availableModels[currentModel]
            ? availableModels[currentModel].name
            : "AI"}{" "}
          | Real-time Crowd Analysis System
        </p>
      </footer>
    </div>
  );
}

export default App;
