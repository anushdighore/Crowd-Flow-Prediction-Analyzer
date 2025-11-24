import React, { useState, useRef, useEffect } from "react";
import "../../styles/PedestrianTracker.css";
import TrajectoryCanvas from "./TrajectoryCanvas";
import CountDisplay from "./CountDisplay";

function PedestrianTracker() {
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

  // Homography settings
  const [useHomography, setUseHomography] = useState(false);
  const [calibrationPoints, setCalibrationPoints] = useState([]);
  const [worldPoints, setWorldPoints] = useState([]);
  const [calibrationMode, setCalibrationMode] = useState(false);

  // Tracking data
  const [trajectories, setTrajectories] = useState({});
  const [currentCount, setCurrentCount] = useState(0);
  const [uniqueCount, setUniqueCount] = useState(0);

  // Trajectory visualization settings
  const [trajectoryMaxPoints, setTrajectoryMaxPoints] = useState(30);

  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const animationRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        try {
          wsRef.current.send(JSON.stringify({ action: "close" }));
          wsRef.current.close();
        } catch (err) {
          console.error("Cleanup error:", err);
        }
      }

      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
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
      setTrajectories({});

      const url = URL.createObjectURL(file);
      setVideoUrl(url);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      const element = containerRef.current;
      if (element.requestFullscreen) {
        element.requestFullscreen().catch((err) => {
          console.error("Error requesting fullscreen:", err);
        });
      } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else if (document.webkitFullscreenElement) {
        document.webkitExitFullscreen();
      }
      setIsFullscreen(false);
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        setIsFullscreen(false);
      }
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("webkitfullscreenchange", handleFullscreenChange);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.removeEventListener(
        "webkitfullscreenchange",
        handleFullscreenChange
      );
    };
  }, []);

  // WebSocket connection
  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const ws = new WebSocket("ws://localhost:8000/ws/pedestrian-track");

      const timeout = setTimeout(() => {
        reject(new Error("WebSocket connection timeout"));
      }, 5000);

      ws.onopen = () => {
        console.log("✅ WebSocket connected for pedestrian tracking");
        clearTimeout(timeout);
        setError(null);

        // Send configuration
        const config = {
          homography: useHomography
            ? {
                image_points: calibrationPoints,
                world_points: worldPoints,
              }
            : null,
          model_path: "yolov8n.pt",
          trajectory_max_points: trajectoryMaxPoints,
          trajectory_max_distance_cm: 2.0,
        };

        ws.send(JSON.stringify(config));
        wsRef.current = ws;
        resolve();
      };

      ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        clearTimeout(timeout);
        reject(error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.status === "ready") {
            console.log("✅ Backend ready for tracking");
            return;
          }

          if (data.success) {
            setCurrentCount(data.count);
            setUniqueCount(data.unique_count);

            if (data.trajectories) {
              setTrajectories(data.trajectories);
            }

            if (data.frame) {
              const img = new Image();
              img.onload = () => {
                const canvas = canvasRef.current;
                if (canvas) {
                  const ctx = canvas.getContext("2d");
                  ctx.drawImage(img, 0, 0);
                }
              };
              img.src = data.frame;
            }
          } else if (data.error) {
            console.error("Tracking error:", data.error);
          }
        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        wsRef.current = null;
        setProcessing(false);
      };
    });
  };

  // Extract and send frames
  const processVideoFrames = async () => {
    if (!videoRef.current) {
      setError("Video reference not available");
      return;
    }

    try {
      setProcessing(true);
      setError(null);

      // Connect WebSocket
      await connectWebSocket();

      const video = videoRef.current;
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const frameRate = fps || 30;
      const frameInterval = 1000 / frameRate;
      let lastFrameTime = 0;
      let frameCount = 0;

      const sendNextFrame = () => {
        const currentTime = video.currentTime * 1000;

        if (currentTime - lastFrameTime >= frameInterval && !video.paused) {
          ctx.drawImage(video, 0, 0);

          // Convert to base64
          canvas.toBlob((blob) => {
            const reader = new FileReader();
            reader.onload = () => {
              if (
                wsRef.current &&
                wsRef.current.readyState === WebSocket.OPEN
              ) {
                wsRef.current.send(
                  JSON.stringify({
                    frame: reader.result,
                    max_trajectory_points: trajectoryMaxPoints,
                    frame_number: frameCount,
                  })
                );
              }
            };
            reader.readAsDataURL(blob);
          }, "image/jpeg");

          lastFrameTime = currentTime;
          frameCount++;
        }

        if (!video.paused && video.currentTime < video.duration) {
          animationRef.current = requestAnimationFrame(sendNextFrame);
        } else {
          console.log(
            `✅ Video processing complete: ${frameCount} frames sent`
          );
          setProcessing(false);

          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: "close" }));
          }
        }
      };

      video.play();
      animationRef.current = requestAnimationFrame(sendNextFrame);
    } catch (err) {
      console.error("❌ Error processing video:", err);
      setError(`Processing error: ${err.message}`);
      setProcessing(false);
    }
  };

  // Handle video metadata loaded
  const handleVideoMetadataLoaded = () => {
    if (videoRef.current) {
      const video = videoRef.current;
      setTotalFrames(Math.round(video.duration * (fps || 30)));
      setFps(fps || 30);
      console.log(
        `📊 Video loaded: ${video.videoWidth}x${video.videoHeight}, duration: ${video.duration}s`
      );
    }
  };

  // Handle play button
  const handleStartProcessing = async () => {
    if (!selectedFile) {
      setError("Please select a video file first");
      return;
    }

    if (
      useHomography &&
      (calibrationPoints.length < 4 || worldPoints.length < 4)
    ) {
      setError("Please select 4 calibration points and enter world distances");
      return;
    }

    await processVideoFrames();
  };

  // Handle pause/resume
  const handlePauseResume = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div
      ref={containerRef}
      className={`pedestrian-tracker ${isFullscreen ? "fullscreen" : ""}`}
    >
      <div className="tracker-header">
        <h2>👥 Pedestrian Tracking</h2>
        <p>
          Track pedestrians in videos with optional world-coordinate
          transformation
        </p>
      </div>

      <div className="tracker-controls">
        <div className="control-section">
          <h3>Video Upload</h3>
          <div className="file-upload">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />
            <button
              onClick={handleUploadClick}
              className="upload-btn"
              disabled={processing}
            >
              📁 Select Video
            </button>
            {selectedFile && (
              <span className="file-name">{selectedFile.name}</span>
            )}
          </div>
        </div>

        <div className="control-section">
          <h3>Homography Settings</h3>
          <label>
            <input
              type="checkbox"
              checked={useHomography}
              onChange={(e) => setUseHomography(e.target.checked)}
            />
            Use World Coordinates (Optional)
          </label>
          {useHomography && (
            <div className="homography-info">
              <p>
                ⚠️ Homography calibration not yet implemented in this preview.
              </p>
              <p>Video will be tracked using image coordinates.</p>
            </div>
          )}
        </div>

        <div className="control-section">
          <h3>Trajectory Visualization</h3>
          <div className="trajectory-control">
            <label htmlFor="trajectory-slider">
              Trajectory Length:{" "}
              <span className="trajectory-value">
                {trajectoryMaxPoints} points
              </span>
            </label>
            <input
              id="trajectory-slider"
              type="range"
              min="5"
              max="100"
              value={trajectoryMaxPoints}
              onChange={(e) => setTrajectoryMaxPoints(parseInt(e.target.value))}
              className="trajectory-slider"
              title="Increase to show longer history (max 2cm in real-world coordinates)"
            />
            <small>
              Shows last N points in trajectory (increase for longer history)
            </small>
          </div>
        </div>

        <div className="action-buttons">
          <button
            onClick={handleStartProcessing}
            disabled={!selectedFile || processing}
            className="start-btn"
          >
            {processing ? "⏳ Processing..." : "🎬 Start Tracking"}
          </button>

          {isPlaying && (
            <button onClick={handlePauseResume} className="pause-btn">
              ⏸ Pause
            </button>
          )}

          <button
            onClick={toggleFullscreen}
            className="fullscreen-btn"
            title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
          >
            {isFullscreen ? "⛔ Exit Fullscreen" : "🖥️ Fullscreen"}
          </button>
        </div>

        {error && <div className="error-message">❌ {error}</div>}
      </div>

      {videoUrl && (
        <div className="tracker-display">
          <div className="video-section">
            <h3>Video Preview</h3>
            <video
              ref={videoRef}
              src={videoUrl}
              width="100%"
              controls
              onLoadedMetadata={handleVideoMetadataLoaded}
              style={{ borderRadius: "8px", maxHeight: "400px" }}
            />
          </div>

          <div className="canvas-section">
            <h3>Tracking Results</h3>
            <canvas
              ref={canvasRef}
              className="tracking-canvas"
              style={{
                border: "2px solid #667eea",
                borderRadius: "8px",
                maxHeight: "400px",
              }}
            />
          </div>

          <div className="stats-section">
            <h3>Tracking Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <label>Current Count</label>
                <div className="stat-value">{currentCount}</div>
              </div>
              <div className="stat-card">
                <label>Unique Persons</label>
                <div className="stat-value">{uniqueCount}</div>
              </div>
              <div className="stat-card">
                <label>Trajectories</label>
                <div className="stat-value">
                  {Object.keys(trajectories).length}
                </div>
              </div>
              <div className="stat-card">
                <label>Status</label>
                <div className="stat-value">
                  {processing ? "🔄 Processing" : "✅ Ready"}
                </div>
              </div>
            </div>
          </div>

          {trajectories && Object.keys(trajectories).length > 0 && (
            <div className="trajectories-section">
              <h3>Trajectory Data</h3>
              <div className="trajectories-info">
                <p>
                  Tracking {Object.keys(trajectories).length} pedestrian
                  trajectory paths
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PedestrianTracker;
