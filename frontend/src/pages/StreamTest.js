import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function StreamTest() {
  const navigate = useNavigate();

  // State
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState("Ready");
  const [count, setCount] = useState(0);
  const [fps, setFps] = useState(0);
  const [error, setError] = useState(null);

  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Cleanup
  useEffect(() => {
    return () => {
      stopEverything();
    };
  }, []);

  const stopEverything = () => {
    console.log("🧹 Cleanup...");
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const startWebcam = async () => {
    try {
      setStatus("Requesting webcam...");
      console.log("📹 Requesting webcam access");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;

        // Wait for video to be ready
        await new Promise((resolve) => {
          videoRef.current.onloadedmetadata = () => {
            console.log("✅ Video metadata loaded");
            videoRef.current.play();
            resolve();
          };
        });
      }

      setStatus("Webcam ready");
      console.log("✅ Webcam started");
      return true;
    } catch (err) {
      const msg = `Webcam error: ${err.message}`;
      setError(msg);
      setStatus(msg);
      console.error("❌", err);
      return false;
    }
  };

  const captureAndSend = async () => {
    if (!videoRef.current || !canvasRef.current) {
      console.warn("⚠️ Missing refs");
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to blob
      const blob = await new Promise((resolve) => {
        canvas.toBlob(resolve, "image/jpeg", 0.8);
      });

      // Create FormData
      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      // Send to CSRNet endpoint
      const response = await fetch(
        "http://localhost:8000/api/v1/csrnet/webcam",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("📨 Received:", data);

      if (data.status === "success") {
        setCount(Math.round(data.count || 0));
        setFps(data.fps || 0);
        setStatus(
          `Processing - Count: ${Math.round(
            data.count || 0
          )} (${data.inference_time_ms.toFixed(0)}ms)`
        );
      } else {
        console.error("⚠️ Processing error:", data);
        setError(data.error || "Unknown error");
      }
    } catch (err) {
      console.error("❌ Request error:", err);
      setError(`Request failed: ${err.message}`);
    }
  };

  const handleStart = async () => {
    console.log("🚀 START CLICKED");
    setError(null);

    // Start webcam
    const webcamOk = await startWebcam();
    if (!webcamOk) {
      console.error("❌ Failed to start webcam");
      return;
    }

    // Wait a bit for video to stabilize
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Start capturing
    console.log("📤 Starting capture loop (CSRNet REST API)");
    setStatus("Streaming...");
    intervalRef.current = setInterval(captureAndSend, 500); // 2 FPS for REST API
    setIsStreaming(true);
    console.log("✅ Streaming started");
  };

  const handleStop = () => {
    console.log("⏹️ STOP CLICKED");
    stopEverything();
    setIsStreaming(false);
    setStatus("Stopped");
    setCount(0);
    setFps(0);
    console.log("✅ Stopped");
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ margin: 0 }}>🧪 Stream Test Page</h1>
        <p style={{ color: "#666", margin: "0.5rem 0 0 0" }}>
          Simple test page to debug webcam streaming
        </p>
        <button
          onClick={() => navigate("/")}
          style={{
            marginTop: "1rem",
            padding: "0.5rem 1rem",
            background: "#6b7280",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          ← Back to Home
        </button>
      </div>

      {/* Status Panel */}
      <div
        style={{
          padding: "1.5rem",
          background: "#f3f4f6",
          borderRadius: "8px",
          marginBottom: "2rem",
          fontFamily: "monospace",
          fontSize: "0.9rem",
        }}
      >
        <h3 style={{ margin: "0 0 1rem 0" }}>📊 Status</h3>
        <div>
          <strong>Status:</strong> {status}
        </div>
        <div>
          <strong>Streaming:</strong> {isStreaming ? "🟢 YES" : "⚫ NO"}
        </div>
        <div>
          <strong>Webcam:</strong>{" "}
          {videoRef.current?.readyState === 2
            ? "✅ Ready"
            : `State ${videoRef.current?.readyState || "N/A"}`}
        </div>
        <div>
          <strong>Endpoint:</strong> CSRNet REST API
        </div>
        <div>
          <strong>Count:</strong> {count}
        </div>
        <div>
          <strong>FPS:</strong> {fps.toFixed(1)}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div
          style={{
            padding: "1rem",
            background: "#fee2e2",
            border: "2px solid #ef4444",
            borderRadius: "8px",
            color: "#dc2626",
            marginBottom: "2rem",
          }}
        >
          <strong>⚠️ Error:</strong> {error}
        </div>
      )}

      {/* Controls */}
      <div style={{ marginBottom: "2rem" }}>
        <button
          onClick={handleStart}
          disabled={isStreaming}
          style={{
            padding: "1rem 2rem",
            fontSize: "1.1rem",
            background: isStreaming ? "#9ca3af" : "#10b981",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: isStreaming ? "not-allowed" : "pointer",
            marginRight: "1rem",
            fontWeight: "600",
          }}
        >
          🎬 Start Streaming
        </button>
        <button
          onClick={handleStop}
          disabled={!isStreaming}
          style={{
            padding: "1rem 2rem",
            fontSize: "1.1rem",
            background: !isStreaming ? "#9ca3af" : "#ef4444",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: !isStreaming ? "not-allowed" : "pointer",
            fontWeight: "600",
          }}
        >
          ⏹️ Stop Streaming
        </button>
      </div>

      {/* Video Display */}
      <div
        style={{
          background: "white",
          borderRadius: "12px",
          padding: "1.5rem",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        <h3 style={{ margin: "0 0 1rem 0" }}>📹 Live Feed</h3>
        <div
          style={{
            position: "relative",
            width: "100%",
            maxWidth: "800px",
            paddingBottom: "56.25%",
            background: "#000",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
          {!isStreaming && (
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                color: "white",
                fontSize: "1.5rem",
                fontWeight: "600",
              }}
            >
              Click "Start Streaming" to begin
            </div>
          )}
        </div>
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {/* Instructions */}
      <div
        style={{
          marginTop: "2rem",
          padding: "1.5rem",
          background: "#eff6ff",
          borderRadius: "8px",
          border: "1px solid #3b82f6",
        }}
      >
        <h3 style={{ margin: "0 0 1rem 0", color: "#1e40af" }}>
          📝 Instructions
        </h3>
        <ol style={{ margin: 0, paddingLeft: "1.5rem", color: "#1e3a8a" }}>
          <li>Open browser DevTools (F12) and go to Console tab</li>
          <li>Click "Start Streaming" button above</li>
          <li>Allow webcam access when prompted</li>
          <li>Watch console for logs and status panel for updates</li>
          <li>You should see count and FPS updating</li>
        </ol>
        <div style={{ marginTop: "1rem", color: "#1e3a8a" }}>
          <strong>Expected logs:</strong>
          <pre
            style={{
              background: "white",
              padding: "1rem",
              borderRadius: "4px",
              marginTop: "0.5rem",
              fontSize: "0.85rem",
            }}
          >
            {`🚀 START CLICKED
📹 Requesting webcam access
✅ Video metadata loaded
✅ Webcam started
📤 Starting capture loop (CSRNet REST API)
✅ Streaming started
📨 Received: {status: "success", count: X, inference_time_ms: Y}`}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default StreamTest;
