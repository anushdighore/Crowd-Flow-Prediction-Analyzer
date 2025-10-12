import React, { useState, useRef, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

export default function ExternalCam() {
  const [cameraUrl, setCameraUrl] = useState("http://192.168.1.6:8080/video");
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [count, setCount] = useState(null);
  const [inferenceTime, setInferenceTime] = useState(null);

  const imgRef = useRef(null);
  const processInterval = useRef(null);

  const stopStream = () => {
    setIsStreaming(false);
    setCount(null);
    setInferenceTime(null);

    if (imgRef.current) {
      imgRef.current.onerror = null;
      imgRef.current.onload = null;
      imgRef.current.src = "";
    }

    if (processInterval.current) {
      clearInterval(processInterval.current);
      processInterval.current = null;
    }
  };

  useEffect(() => {
    return () => stopStream();
  }, []);

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

  const processFrame = async () => {
    try {
      const res = await fetch(
        `${API_BASE}/camera/process?camera_url=${encodeURIComponent(cameraUrl)}`
      );
      const data = await res.json();
      if (res.ok) {
        setCount(data.count ?? null);
        setInferenceTime(data.inference_time_ms ?? null);
      }
    } catch (err) {
      console.error('Frame processing error:', err);
    }
  };

  const startMjpegStream = () => {
    if (!imgRef.current) {
      console.error("Image ref not available");
      setError("Image element not ready");
      return;
    }

    const streamSrc = `${API_BASE}/camera/stream?camera_url=${encodeURIComponent(cameraUrl)}`;
    
    console.log("🎥 Starting MJPEG stream...");
    console.log("   Stream URL:", streamSrc);
    console.log("   Camera URL:", cameraUrl);
    console.log("   Image element:", imgRef.current);

    // Set up event handlers BEFORE setting src
    imgRef.current.onload = () => {
      console.log("✅ MJPEG stream loaded successfully!");
      setError(null);
      setIsStreaming(true);
    };

    imgRef.current.onerror = (e) => {
      console.error("❌ MJPEG stream error:", e);
      console.error("   Failed URL:", streamSrc);
      setError("MJPEG stream failed to load. Check if backend is running and camera is accessible.");
      setIsStreaming(false);
    };

    // Set the source to start streaming
    imgRef.current.src = streamSrc;
    console.log("   Image src set, waiting for load...");
  };

  const startStream = async () => {
    if (!cameraUrl) {
      setError("Please enter a valid camera URL");
      return;
    }
    
    console.log("📹 Start Stream clicked");
    console.log("   Camera URL:", cameraUrl);
    
    setLoading(true);
    setError(null);
    stopStream();
    
    try {
      // Show the streaming section immediately
      setIsStreaming(true);
      
      // Small delay to ensure DOM is ready
      setTimeout(() => {
        startMjpegStream();
      }, 100);
      
      setLoading(false);
    } catch (e) {
      console.error("Start stream error:", e);
      setError(e.message);
      stopStream();
      setLoading(false);
    }
  };

  return (
    <>
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <h1 style={{ color: "#333", marginBottom: "20px" }}>External Camera - MJPEG Streaming</h1>

        <div style={{ background: "#f5f5f5", padding: "20px", borderRadius: "8px", marginBottom: "20px" }}>
          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold", color: "#555" }}>
              Camera URL:
            </label>
            <input
              type="text"
              value={cameraUrl}
              onChange={(e) => setCameraUrl(e.target.value)}
              placeholder="http://192.168.1.6:8080/video"
              disabled={isStreaming}
              style={{
                width: "100%",
                padding: "10px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontSize: "14px",
                boxSizing: "border-box",
                background: isStreaming ? "#e9ecef" : "white"
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
            <button
              onClick={testConnection}
              disabled={loading || isStreaming}
              style={{
                padding: "10px 20px",
                border: "none",
                borderRadius: "4px",
                cursor: loading || isStreaming ? "not-allowed" : "pointer",
                fontSize: "14px",
                fontWeight: "500",
                background: "#007bff",
                color: "white",
                opacity: loading || isStreaming ? 0.6 : 1
              }}
            >
              Test Camera
            </button>
            {!isStreaming ? (
              <button
                onClick={startStream}
                disabled={loading}
                style={{
                  padding: "10px 20px",
                  border: "none",
                  borderRadius: "4px",
                  cursor: loading ? "not-allowed" : "pointer",
                  fontSize: "14px",
                  fontWeight: "500",
                  background: "#28a745",
                  color: "white",
                  opacity: loading ? 0.6 : 1
                }}
              >
                {loading ? "Starting..." : "Start Stream"}
              </button>
            ) : (
              <button
                onClick={stopStream}
                style={{
                  padding: "10px 20px",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "500",
                  background: "#dc3545",
                  color: "white"
                }}
              >
                Stop Stream
              </button>
            )}
          </div>

          {error && (
            <div style={{
              color: "#721c24",
              background: "#f8d7da",
              padding: "12px",
              borderRadius: "4px",
              border: "1px solid #f5c6cb"
            }}>
              Error: {error}
            </div>
          )}
        </div>

        {isStreaming && (
          <div style={{
            background: "white",
            padding: "20px",
            borderRadius: "8px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            marginBottom: "20px"
          }}>
            <h2 style={{ marginTop: 0, color: "#333" }}>Live Stream</h2>
            <div style={{ 
              background: "#000", 
              borderRadius: "8px", 
              overflow: "hidden", 
              marginBottom: "15px",
              minHeight: "480px"
            }}>
              <img
                ref={imgRef}
                alt="Camera stream"
                style={{
                  width: "100%",
                  height: "auto",
                  maxHeight: "480px",
                  objectFit: "contain",
                  display: "block"
                }}
              />
            </div>
            <div style={{
              background: "#f8f9fa",
              padding: "15px",
              borderRadius: "4px",
              borderLeft: "4px solid #28a745"
            }}>
              <p style={{ margin: "8px 0", color: "#555" }}>
                <strong>✅ Stream Status:</strong> <span style={{ color: "#28a745", fontWeight: "bold" }}>Active</span>
              </p>
              <p style={{ margin: "8px 0", color: "#555" }}>
                <strong>Stream Type:</strong> MJPEG (Direct Feed)
              </p>
              <p style={{ margin: "8px 0", color: "#555" }}>
                <strong>Camera URL:</strong> <code style={{ background: "#e9ecef", padding: "2px 6px", borderRadius: "3px", fontSize: "13px" }}>{cameraUrl}</code>
              </p>
            </div>
          </div>
        )}

        <div style={{
          background: "#fff3cd",
          padding: "20px",
          borderRadius: "8px",
          borderLeft: "4px solid #ffc107"
        }}>
          <h3 style={{ marginTop: 0, color: "#856404" }}>Instructions:</h3>
          <ol style={{ margin: "10px 0", paddingLeft: "25px", color: "#856404" }}>
            <li style={{ margin: "8px 0" }}>Enter your IP camera URL (e.g., http://192.168.1.6:8080/video)</li>
            <li style={{ margin: "8px 0" }}>Click "Test Camera" to verify connection</li>
            <li style={{ margin: "8px 0" }}>Click "Start Stream" to begin streaming</li>
            <li style={{ margin: "8px 0" }}>The stream will display with real-time crowd counting</li>
            <li style={{ margin: "8px 0" }}>Use "Stop Stream" to end the streaming session</li>
          </ol>
          <h4 style={{ color: "#856404" }}>Common Camera URLs:</h4>
          <ul style={{ margin: "10px 0", paddingLeft: "25px", color: "#856404" }}>
            <li style={{ margin: "8px 0" }}><strong>IP Webcam:</strong> http://192.168.1.6:8080/video</li>
            <li style={{ margin: "8px 0" }}><strong>DroidCam:</strong> http://192.168.1.6:4747/video</li>
            <li style={{ margin: "8px 0" }}><strong>Snapshot:</strong> http://192.168.1.6:8080/shot.jpg</li>
          </ul>
        </div>
      </div>
    </>
  );
}
