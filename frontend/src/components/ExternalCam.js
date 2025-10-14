import React, { useState, useRef, useEffect, useCallback } from "react";
import "./WebcamCounter.css";

const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000";

export default function ExternalCam() {
  const [cameraUrl, setCameraUrl] = useState("http://192.168.137.168:8080/video");
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [fps, setFps] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [selectedModel, setSelectedModel] = useState("csrnet");

  const imgRef = useRef(null);
  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Stop streaming
  const stopStream = useCallback(() => {
    setIsStreaming(false);
    setResults(null);
    setFps(0);
    setFrameCount(0);
    disconnectWebSocket();
  }, [disconnectWebSocket]);

  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  const testConnection = async () => {
    try {
      setError(null);
      const res = await fetch(
        `${API_BASE}/camera/test-connection?camera_url=${encodeURIComponent(cameraUrl)}`
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || data.message || "Failed to connect to camera");
      }
      alert(`Camera test successful!\nResponse time: ${data.response_time_seconds}s\nImage size: ${data.image_dimensions}`);
    } catch (err) {
      console.error('Camera test error:', err);
      setError(`Camera test failed: ${err.message}`);
    }
  };

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(`${WS_BASE}/ws/external-camera`);

      ws.onopen = () => {
        console.log("✅ External camera WebSocket connected");
        setError(null);
        
        // Send camera URL and model selection
        ws.send(JSON.stringify({
          camera_url: cameraUrl,
          model: selectedModel
        }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.success) {
          if (data.frame) {
            // Update image with new frame
            if (imgRef.current) {
              imgRef.current.src = data.frame;
            }
          }
          
          // Update results
          if (data.count !== undefined) {
            setResults(data);
            setFps(data.fps || 0);
            setFrameCount(data.frame_number || 0);
          }
        } else {
          console.error("Processing error:", data.error);
          setError(data.error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("❌ External camera WebSocket disconnected");
        if (isStreaming) {
          setError("Connection lost. Please restart.");
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(`Failed to connect to server: ${err.message}`);
    }
  }, [cameraUrl, selectedModel, isStreaming]);

  // Request frames from backend
  const requestFrame = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "get_frame" }));
    }
  }, []);

  // Start streaming
  const startStream = useCallback(async () => {
    if (!cameraUrl) {
      setError("Please enter a valid camera URL");
      return;
    }
    
    console.log("📹 Starting external camera stream");
    console.log("   Camera URL:", cameraUrl);
    console.log("   Model:", selectedModel);
    
    setLoading(true);
    setError(null);
    stopStream();
    
    try {
      setIsStreaming(true);
      connectWebSocket();
      
      // Request frames at ~5 FPS (200ms interval)
      intervalRef.current = setInterval(requestFrame, 200);
      
      setLoading(false);
    } catch (e) {
      console.error("Start stream error:", e);
      setError(e.message);
      stopStream();
      setLoading(false);
    }
  }, [cameraUrl, selectedModel, stopStream, connectWebSocket, requestFrame]);

  return (
    <div className="webcam-counter">
      <div className="container">
        <h1>🎥 External IP Camera with Crowd Counting</h1>

        <div className="controls-panel">
          <div className="input-group">
            <label>Camera URL:</label>
            <input
              type="text"
              value={cameraUrl}
              onChange={(e) => setCameraUrl(e.target.value)}
              placeholder="http://192.168.137.168:8080/video"
              disabled={isStreaming}
              className={isStreaming ? "disabled" : ""}
            />
          </div>

          <div className="input-group">
            <label>Select Model:</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={isStreaming}
              className={isStreaming ? "disabled" : ""}
            >
              <option value="csrnet">CSRNet</option>
              <option value="tmtb">TMTB (VMamba)</option>
            </select>
          </div>

          <div className="button-group">
            <button
              onClick={testConnection}
              disabled={loading || isStreaming}
              className="btn btn-test"
            >
              🔍 Test Camera
            </button>
            {!isStreaming ? (
              <button
                onClick={startStream}
                disabled={loading}
                className="btn btn-start"
              >
                {loading ? "⏳ Starting..." : "▶️ Start Stream"}
              </button>
            ) : (
              <button onClick={stopStream} className="btn btn-stop">
                ⏹️ Stop Stream
              </button>
            )}
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {isStreaming && (
          <div className="video-section">
            <div className="video-container">
              <img ref={imgRef} alt="External camera stream" className="video-feed" />
              {results && (
                <div className="overlay">
                  <div className="count-display">
                    👥 Count: <span className="count-number">{results.count}</span>
                  </div>
                </div>
              )}
            </div>

            {results && (
              <div className="stats-panel">
                <div className="stat-item">
                  <span className="stat-label">People Count:</span>
                  <span className="stat-value">{results.count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Model:</span>
                  <span className="stat-value">{results.model?.toUpperCase()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Inference Time:</span>
                  <span className="stat-value">{results.inference_time_ms?.toFixed(1)} ms</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">FPS:</span>
                  <span className="stat-value">{fps.toFixed(1)}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Frames Processed:</span>
                  <span className="stat-value">{frameCount}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Device:</span>
                  <span className="stat-value">{results.device}</span>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="info-panel">
          <h3>📋 Instructions</h3>
          <ol>
            <li>Enter your IP camera URL (e.g., http://192.168.137.168:8080/video)</li>
            <li>Select the ML model (CSRNet or TMTB)</li>
            <li>Click "Test Camera" to verify connection</li>
            <li>Click "Start Stream" to begin real-time crowd counting</li>
            <li>View live predictions overlaid on the video stream</li>
          </ol>
          <h4>📱 Common Camera Apps:</h4>
          <ul>
            <li><strong>IP Webcam:</strong> http://YOUR_IP:8080/video</li>
            <li><strong>DroidCam:</strong> http://YOUR_IP:4747/video</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
