import React, { useState, useRef, useEffect, useCallback } from "react";
import "./WebcamCounter.css";

function WebcamCounter() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [fps, setFps] = useState(0);
  const [frameCount, setFrameCount] = useState(0);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Start webcam
  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }

      setError(null);
    } catch (err) {
      setError(`Failed to access webcam: ${err.message}`);
      console.error("Webcam error:", err);
    }
  }, []);

  // Stop webcam
  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket("ws://localhost:8000/ws/count");

      ws.onopen = () => {
        console.log("✅ WebSocket connected");
        setError(null);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.success) {
          setResults(data);
          setFps(data.fps || 0);
          setFrameCount(data.frame_number || 0);
        } else {
          console.error("Processing error:", data.error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("❌ WebSocket disconnected");
        if (isStreaming) {
          setError("Connection lost. Please restart.");
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(`Failed to connect to server: ${err.message}`);
    }
  }, [isStreaming]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Capture and send frame
  const captureAndSendFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current) {
      return;
    }

    // Check if WebSocket is ready
    if (wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");

      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw current video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64
      const frameData = canvas.toDataURL("image/jpeg", 0.8);

      // Send to server
      wsRef.current.send(JSON.stringify({ frame: frameData }));
    } catch (err) {
      console.error("Frame capture error:", err);
    }
  }, []);

  // Start streaming
  const handleStartStreaming = async () => {
    await startWebcam();
    connectWebSocket();

    // Start sending frames (every 100ms = ~10 FPS)
    intervalRef.current = setInterval(captureAndSendFrame, 100);

    setIsStreaming(true);
    setResults(null);
  };

  // Stop streaming
  const handleStopStreaming = () => {
    // Clear interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Disconnect WebSocket
    disconnectWebSocket();

    // Stop webcam
    stopWebcam();

    setIsStreaming(false);
    setResults(null);
    setFps(0);
    setFrameCount(0);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      disconnectWebSocket();
      stopWebcam();
    };
  }, [disconnectWebSocket, stopWebcam]);

  return (
    <div className="webcam-counter">
      <div className="webcam-header">
        <h2>🎥 Real-Time Webcam Crowd Counter</h2>
        <p>Live crowd counting using your webcam</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="webcam-container">
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="webcam-video"
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />

          {isStreaming && results && (
            <div className="video-overlay">
              <div className="count-badge">
                <span className="count-label">Count:</span>
                <span className="count-value">{results.count}</span>
              </div>
              <div className="fps-badge">
                <span className="fps-value">{fps.toFixed(1)} FPS</span>
              </div>
            </div>
          )}

          {!isStreaming && (
            <div className="video-placeholder">
              <div className="placeholder-content">
                <div className="camera-icon">📹</div>
                <p>Click "Start" to begin webcam streaming</p>
              </div>
            </div>
          )}
        </div>

        <div className="webcam-controls">
          {!isStreaming ? (
            <button onClick={handleStartStreaming} className="btn btn-start">
              🎬 Start Streaming
            </button>
          ) : (
            <button onClick={handleStopStreaming} className="btn btn-stop">
              ⏹️ Stop Streaming
            </button>
          )}
        </div>
      </div>

      {isStreaming && results && (
        <div className="results-panel">
          <div className="result-card">
            <h3>📊 Live Results</h3>

            <div className="result-grid">
              <div className="result-item">
                <span className="result-label">Detected Count:</span>
                <span className="result-value large">{results.count}</span>
              </div>

              <div className="result-item">
                <span className="result-label">Frames Processed:</span>
                <span className="result-value">{frameCount}</span>
              </div>

              <div className="result-item">
                <span className="result-label">Processing FPS:</span>
                <span className="result-value">{fps.toFixed(2)}</span>
              </div>

              {results.timing && (
                <>
                  <div className="result-item">
                    <span className="result-label">Inference Time:</span>
                    <span className="result-value">
                      {results.timing.inference_ms.toFixed(1)} ms
                    </span>
                  </div>

                  <div className="result-item">
                    <span className="result-label">Total Time:</span>
                    <span className="result-value">
                      {results.timing.total_ms.toFixed(1)} ms
                    </span>
                  </div>
                </>
              )}
            </div>

            {results.reasoning && (
              <div className="reasoning-section">
                <h4>🧠 Model Reasoning:</h4>
                <p>{results.reasoning}</p>
              </div>
            )}

            {results.density_map_stats && (
              <div className="stats-section">
                <h4>📈 Density Map Statistics:</h4>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span>Max:</span>
                    <span>{results.density_map_stats.max.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span>Mean:</span>
                    <span>{results.density_map_stats.mean.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span>Sum:</span>
                    <span>{results.density_map_stats.sum.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="webcam-info">
        <h3>ℹ️ How it works</h3>
        <ol>
          <li>Click "Start Streaming" to activate your webcam</li>
          <li>Frames are captured and sent to the server for processing</li>
          <li>The VMamba-TMTB model analyzes each frame in real-time</li>
          <li>Crowd count is displayed with performance metrics</li>
          <li>Click "Stop Streaming" when done</li>
        </ol>

        <div className="tips">
          <h4>💡 Tips for best results:</h4>
          <ul>
            <li>Ensure good lighting conditions</li>
            <li>Position camera to capture the full area of interest</li>
            <li>Keep camera stable for consistent results</li>
            <li>Processing speed depends on your hardware (GPU recommended)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default WebcamCounter;
