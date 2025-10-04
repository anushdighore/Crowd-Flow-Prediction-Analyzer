import React, { useState, useRef } from "react";
import "./App.css";
import WebcamCounter from "./WebcamCounter";

function App() {
  const [mode, setMode] = useState("upload"); // "upload" or "webcam"
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

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
      <header className="app-header">
        <h1>🧠 VMamba-TMTB Crowd Counter</h1>
        <p>Advanced crowd counting using Visual State Space Models</p>

        {/* Mode Selector */}
        <div className="mode-selector">
          <button
            className={`mode-btn ${mode === "upload" ? "active" : ""}`}
            onClick={() => setMode("upload")}
          >
            📤 Upload Image
          </button>
          <button
            className={`mode-btn ${mode === "webcam" ? "active" : ""}`}
            onClick={() => setMode("webcam")}
          >
            🎥 Live Webcam
          </button>
        </div>
      </header>

      <main className="app-main">
        {mode === "webcam" ? (
          <WebcamCounter />
        ) : (
          <>
            {/* Upload Section */}
            <div className="upload-section">
              <div
                className={`drop-zone ${selectedFile ? "has-file" : ""}`}
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
                      <p>📸 {selectedFile.name}</p>
                      <p>
                        Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="drop-zone-content">
                    <div className="upload-icon">📁</div>
                    <p>Drag & drop an image here, or click to select</p>
                    <small>Supports JPEG, PNG, BMP, TIFF (max 10MB)</small>
                  </div>
                )}
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
              />

              <div className="action-buttons">
                <button
                  onClick={handleSubmit}
                  disabled={!selectedFile || loading}
                  className="count-button"
                >
                  {loading ? "🔄 Processing..." : "🧮 Count Crowd"}
                </button>

                <button
                  onClick={handleReset}
                  disabled={loading}
                  className="reset-button"
                >
                  🗑️ Reset
                </button>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-section">
                <div className="error-message">❌ {error}</div>
              </div>
            )}

            {/* Results Section */}
            {results && (
              <div className="results-section">
                <div className="results-header">
                  <h2>📊 Crowd Counting Results</h2>
                </div>
                <div className="results-grid">
                  <div className="result-card main-result">
                    <div className="result-value">{results.crowd_count}</div>
                    <div className="result-label">People Detected</div>
                  </div>

                  <div className="result-card">
                    <div className="result-value">
                      {results.processing_time_ms}ms
                    </div>
                    <div className="result-label">Processing Time</div>
                  </div>

                  <div className="result-card">
                    <div className="result-value">
                      {results.image_info?.dimensions || "Unknown"}
                    </div>
                    <div className="result-label">Image Dimensions</div>
                  </div>

                  <div className="result-card">
                    <div className="result-value">
                      {((results.image_info?.size_bytes || 0) / 1024).toFixed(
                        1
                      )}
                      KB
                    </div>
                    <div className="result-label">File Size</div>
                  </div>
                </div>
                {/* Timing Breakdown */}
                {results.timing_breakdown && (
                  <div className="timing-section">
                    <h3>⏱️ Processing Breakdown</h3>
                    <div className="timing-bars">
                      <div className="timing-item">
                        <span>Preprocessing:</span>
                        <div className="timing-bar">
                          <div
                            className="timing-fill preprocess"
                            style={{
                              width: `${
                                (results.timing_breakdown.preprocess_ms /
                                  results.processing_time_ms) *
                                100
                              }%`,
                            }}
                          ></div>
                        </div>
                        <span>{results.timing_breakdown.preprocess_ms}ms</span>
                      </div>

                      <div className="timing-item">
                        <span>Inference:</span>
                        <div className="timing-bar">
                          <div
                            className="timing-fill inference"
                            style={{
                              width: `${
                                (results.timing_breakdown.inference_ms /
                                  results.processing_time_ms) *
                                100
                              }%`,
                            }}
                          ></div>
                        </div>
                        <span>{results.timing_breakdown.inference_ms}ms</span>
                      </div>

                      <div className="timing-item">
                        <span>Postprocessing:</span>
                        <div className="timing-bar">
                          <div
                            className="timing-fill postprocess"
                            style={{
                              width: `${
                                (results.timing_breakdown.postprocess_ms /
                                  results.processing_time_ms) *
                                100
                              }%`,
                            }}
                          ></div>
                        </div>
                        <span>{results.timing_breakdown.postprocess_ms}ms</span>
                      </div>
                    </div>
                  </div>
                )}
                {/* Heatmap Visualization */}
                {results.heatmap_overlay && (
                  <div className="heatmap-section">
                    <h3>🔥 Density Heatmap</h3>
                    <img
                      src={results.heatmap_overlay}
                      alt="Crowd density heatmap"
                      className="heatmap-image"
                    />
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by VMamba-TMTB | Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
