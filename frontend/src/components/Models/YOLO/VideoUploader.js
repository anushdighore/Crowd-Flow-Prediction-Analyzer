import React, { useState, useRef, useEffect } from "react";
import "../../../styles/VideoUploader.css";
import TrajectoryCanvas from "../../Trajectory/TrajectoryCanvas";
import HeatmapOverlay from "../../Heatmap/HeatmapOverlay";
import CountDisplay from "../../CountDisplay";

function VideoUploader() {
  const [selectedModel, setSelectedModel] = useState("yolo-nano");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);
  const [fps, setFps] = useState(0);

  // Feature flags
  const [enableTracking, setEnableTracking] = useState(true);
  const [enableHeatmap, setEnableHeatmap] = useState(true);
  const [autoSwitch, setAutoSwitch] = useState(false);
  const [autoSwitchThreshold, setAutoSwitchThreshold] = useState(30);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const animationRef = useRef(null);

  // Available models
  const models = [
    { id: "yolo-nano", name: "YOLO Nano", description: "Fast detection" },
    { id: "yolo-small", name: "YOLO Small", description: "Balanced" },
    { id: "csrnet", name: "CSRNet", description: "Density estimation" },
    { id: "mcnn", name: "MCNN", description: "High accuracy" },
  ];

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Close WebSocket
      if (wsRef.current) {
        try {
          wsRef.current.send(JSON.stringify({ action: "close" }));
          wsRef.current.close();
        } catch (err) {
          console.error("Cleanup error:", err);
        }
      }

      // Revoke video URL
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith("video/")) {
        setError("Please select a valid video file");
        return;
      }

      setSelectedFile(file);
      setError(null);
      setResults(null);

      // Create video URL for preview
      const url = URL.createObjectURL(file);
      setVideoUrl(url);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // WebSocket connection for video processing
  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return Promise.resolve(); // Already connected
    }

    return new Promise((resolve, reject) => {
      const ws = new WebSocket("ws://localhost:8000/ws/video-process");

      const timeout = setTimeout(() => {
        reject(new Error("WebSocket connection timeout"));
      }, 5000);

      ws.onopen = () => {
        console.log("✅ WebSocket connected for video processing");
        clearTimeout(timeout);
        setError(null);

        // Send configuration
        ws.send(
          JSON.stringify({
            model: selectedModel,
            tracking: enableTracking,
            confidence: confidenceThreshold,
          })
        );

        resolve();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.status === "ready") {
            console.log("📹 Backend ready for video frames");
            return;
          }

          if (data.error || !data.success) {
            setError(data.error || "Processing failed");
            setProcessing(false);
            return;
          }

          // Update results with current frame data
          setResults(data);
          setCurrentFrame(data.frame_number || 0);
          setFps(data.fps || 0);

          // Update video current time if available
          if (videoRef.current && data.timestamp !== undefined) {
            videoRef.current.currentTime = data.timestamp;
          }
        } catch (err) {
          console.error("WebSocket message error:", err);
          setError(`Failed to parse results: ${err.message}`);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        clearTimeout(timeout);
        setError("WebSocket connection failed");
        setProcessing(false);
        reject(error);
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
        setProcessing(false);
      };

      wsRef.current = ws;
    });
  };

  const handleStartProcessing = async () => {
    if (!selectedFile) {
      setError("Please select a video file first");
      return;
    }

    if (!videoRef.current) {
      setError("Video not loaded");
      return;
    }

    setLoading(true);
    setError(null);
    setProcessing(true);
    setResults(null);
    setCurrentFrame(0);

    try {
      console.log("🎬 Starting video processing...");

      // Connect WebSocket and wait for it to be ready
      await connectWebSocket();

      console.log("✅ WebSocket connected, starting frame extraction...");
      setLoading(false);

      // Start processing video frames
      await processVideoFrames();
    } catch (err) {
      console.error("❌ Processing error:", err);
      setError(`Error: ${err.message}`);
      setLoading(false);
      setProcessing(false);
    }
  };

  const processVideoFrames = async () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    // Set canvas size to video dimensions
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const frameInterval = 1000 / 30; // Process at 30 FPS
    let lastFrameTime = 0;
    let frameCount = 0;

    const extractAndSendFrame = async (currentTime) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.log("WebSocket closed, stopping frame extraction");
        setProcessing(false);
        return;
      }

      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to base64
      const frameData = canvas.toDataURL("image/jpeg", 0.8);

      // Send frame to backend
      wsRef.current.send(
        JSON.stringify({
          frame: frameData,
          timestamp: currentTime,
          frame_number: frameCount,
        })
      );

      frameCount++;
      setTotalFrames(frameCount);
    };

    // Handle video playback with frame extraction
    const onTimeUpdate = async () => {
      const currentTime = video.currentTime;

      // Extract frame at intervals
      if (currentTime - lastFrameTime >= frameInterval / 1000) {
        await extractAndSendFrame(currentTime);
        lastFrameTime = currentTime;
      }
    };

    const onEnded = () => {
      console.log("✅ Video processing complete");
      setProcessing(false);
      video.removeEventListener("timeupdate", onTimeUpdate);
      video.removeEventListener("ended", onEnded);

      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({ action: "close" }));
        wsRef.current.close();
      }
    };

    video.addEventListener("timeupdate", onTimeUpdate);
    video.addEventListener("ended", onEnded);

    // Start video playback
    video.currentTime = 0;
    setIsPlaying(true);
    await video.play();
  };

  const handleStopProcessing = () => {
    console.log("⏹️ Stopping video processing...");

    // Stop video playback
    if (videoRef.current) {
      videoRef.current.pause();
    }

    // Close WebSocket
    if (wsRef.current) {
      try {
        wsRef.current.send(JSON.stringify({ action: "close" }));
        wsRef.current.close();
      } catch (err) {
        console.error("Error closing WebSocket:", err);
      }
      wsRef.current = null;
    }

    setProcessing(false);
    setIsPlaying(false);
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleClear = () => {
    handleStopProcessing();
    setSelectedFile(null);
    setVideoUrl(null);
    setResults(null);
    setError(null);
    setCurrentFrame(0);
    setTotalFrames(0);

    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  return (
    <div className="video-uploader">
      <div className="video-header">
        <h2>🎬 Video Crowd Analysis</h2>
        <p>Upload and analyze crowd videos with trajectory tracking</p>
      </div>

      <div className="video-container-main">
        {/* Left Panel: Configuration */}
        <div className="config-panel">
          <section className="model-selection">
            <h3>🤖 Select Model</h3>
            <div className="model-list">
              {models.map((model) => (
                <div
                  key={model.id}
                  className={`model-option ${
                    selectedModel === model.id ? "selected" : ""
                  }`}
                  onClick={() => setSelectedModel(model.id)}
                >
                  <div className="model-name">{model.name}</div>
                  <div className="model-desc">{model.description}</div>
                </div>
              ))}
            </div>
          </section>

          <section className="settings-section">
            <h3>⚙️ Settings</h3>

            <div className="setting-item">
              <label>
                Confidence Threshold:{" "}
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
                className="slider"
              />
            </div>

            <div className="toggle-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={enableTracking}
                  onChange={(e) => setEnableTracking(e.target.checked)}
                />
                <span>🎯 Enable Trajectory Tracking</span>
              </label>

              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={enableHeatmap}
                  onChange={(e) => setEnableHeatmap(e.target.checked)}
                />
                <span>🔥 Show Heatmap/Detection Overlay</span>
              </label>

              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={autoSwitch}
                  onChange={(e) => setAutoSwitch(e.target.checked)}
                />
                <span>🔄 Auto-Switch Models</span>
              </label>
            </div>

            {autoSwitch && (
              <div className="setting-item">
                <label>
                  Auto-Switch Threshold: <strong>{autoSwitchThreshold}</strong>
                </label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={autoSwitchThreshold}
                  onChange={(e) =>
                    setAutoSwitchThreshold(parseInt(e.target.value))
                  }
                  className="slider"
                />
              </div>
            )}
          </section>

          <section className="upload-section">
            <h3>📤 Upload Video</h3>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />

            {!selectedFile ? (
              <div className="upload-box" onClick={handleUploadClick}>
                <div className="upload-icon">🎬</div>
                <h4>Click to upload video</h4>
                <p>MP4, AVI, MOV, etc.</p>
              </div>
            ) : (
              <div className="file-info">
                <p>✅ {selectedFile.name}</p>
                <p className="file-size">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            )}
          </section>

          <div className="action-buttons">
            <button
              onClick={handleUploadClick}
              className="btn btn-secondary"
              disabled={processing}
            >
              📎 {selectedFile ? "Change Video" : "Select Video"}
            </button>
            <button
              onClick={handleStartProcessing}
              className="btn btn-primary"
              disabled={!selectedFile || processing || loading}
            >
              {loading
                ? "🔄 Uploading..."
                : processing
                ? "⏸️ Processing..."
                : "🚀 Start Analysis"}
            </button>
            {processing && (
              <button onClick={handleStopProcessing} className="btn btn-danger">
                ⏹️ Stop
              </button>
            )}
            {(selectedFile || results) && (
              <button
                onClick={handleClear}
                className="btn btn-outline"
                disabled={loading}
              >
                🗑️ Clear
              </button>
            )}
          </div>
        </div>

        {/* Right Panel: Video Display & Results */}
        <div className="display-panel">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {videoUrl && (
            <section className="video-display">
              <h3>📹 Video Preview</h3>
              <div className="video-wrapper" style={{ position: "relative" }}>
                <video
                  ref={videoRef}
                  src={videoUrl}
                  controls
                  className="video-player"
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />

                {/* Trajectory overlay */}
                {processing && (
                  <TrajectoryCanvas
                    sourceRef={videoRef}
                    results={results}
                    enableTracking={enableTracking}
                  />
                )}

                {/* Count overlay */}
                {processing && results && (
                  <CountDisplay
                    results={results}
                    enableTracking={enableTracking}
                    displayMode="overlay"
                    fps={fps}
                    currentModel={results.model}
                    autoSwitch={autoSwitch}
                  />
                )}
              </div>

              {/* Video controls info */}
              {processing && (
                <div className="progress-info">
                  <p>
                    Frame: {currentFrame} / {totalFrames}
                  </p>
                  <p>FPS: {fps.toFixed(1)}</p>
                  {totalFrames > 0 && (
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${(currentFrame / totalFrames) * 100}%`,
                        }}
                      />
                    </div>
                  )}
                </div>
              )}
            </section>
          )}

          {/* Heatmap Display */}
          {processing && enableHeatmap && (
            <HeatmapOverlay
              heatmapImage={results?.heatmap}
              enableHeatmap={enableHeatmap}
              modelType={selectedModel}
              displayMode="standalone"
            />
          )}

          {/* Statistics Panel */}
          {processing && results && (
            <section className="stats-section">
              <h3>📊 Analysis Statistics</h3>
              <CountDisplay
                results={results}
                enableTracking={enableTracking}
                displayMode="stats"
                fps={fps}
                currentModel={results.model}
              />

              {/* Speed Statistics (if tracking enabled) */}
              {enableTracking && results.speed_stats && (
                <div className="speed-stats">
                  <h4>🚶 Movement Analysis</h4>
                  <div className="stat-grid">
                    <div className="stat-card">
                      <span className="stat-label">Avg Speed</span>
                      <span className="stat-value">
                        {results.speed_stats.average_speed?.toFixed(2) || 0}{" "}
                        px/s
                      </span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Max Speed</span>
                      <span className="stat-value">
                        {results.speed_stats.max_speed?.toFixed(2) || 0} px/s
                      </span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Min Speed</span>
                      <span className="stat-value">
                        {results.speed_stats.min_speed?.toFixed(2) || 0} px/s
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Track History Table */}
              {enableTracking &&
                results.tracks &&
                results.tracks.length > 0 && (
                  <div className="tracks-section">
                    <h4>🎯 Active Tracks</h4>
                    <div className="tracks-table">
                      <div className="table-header">
                        <div>Track ID</div>
                        <div>State</div>
                        <div>Frames</div>
                        <div>Speed</div>
                      </div>
                      {results.tracks.slice(0, 10).map((track) => (
                        <div key={track.id} className="table-row">
                          <div>#{track.id}</div>
                          <div>
                            <span
                              className={`state-badge state-${track.state}`}
                            >
                              {track.state === 0
                                ? "NEW"
                                : track.state === 1
                                ? "TRACKED"
                                : "LOST"}
                            </span>
                          </div>
                          <div>{track.frames_tracked || 0}</div>
                          <div>{track.speed?.toFixed(1) || 0} px/s</div>
                        </div>
                      ))}
                    </div>
                    {results.tracks.length > 10 && (
                      <p className="more-tracks">
                        + {results.tracks.length - 10} more tracks
                      </p>
                    )}
                  </div>
                )}
            </section>
          )}

          {!videoUrl && (
            <div className="placeholder">
              <div className="placeholder-icon">🎬</div>
              <h3>No video selected</h3>
              <p>Upload a video to start crowd analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default VideoUploader;
