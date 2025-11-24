// frontend/src/components/Camera/HLSStreamingPage.js
import React, { useState, useEffect } from "react";
import HLSPlayer from "../HLSPlayer";

const HLSStreamingPage = () => {
  const [streamId, setStreamId] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [streamUrl, setStreamUrl] = useState("");
  const [cameraUrl, setCameraUrl] = useState("http://192.168.1.6:8080/video");

  const API_BASE_URL = "http://localhost:8000/api";

  // Start HLS stream
  const startStream = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/camera/hls/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          camera_url: cameraUrl,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || `Failed to start stream: ${response.status}`
        );
      }

      const data = await response.json();
      setStreamId(data.stream_id);

      // Use the manifest_url from response or construct it
      const manifestUrl =
        data.manifest_url ||
        `/api/camera/hls/playlist/${data.stream_id}/playlist.m3u8`;
      setStreamUrl(`http://localhost:8000${manifestUrl}`);
      setIsStreaming(true);

      console.log("Stream started:", data);
      console.log("Manifest URL:", manifestUrl);
    } catch (err) {
      console.error("Error starting stream:", err);
      setError(err.message);
    }
  };

  // Stop HLS stream
  const stopStream = async () => {
    if (!streamId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/camera/hls/stop/${streamId}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to stop stream: ${response.status}`);
      }

      setIsStreaming(false);
      setStreamId(null);
      setStreamUrl("");
      console.log("Stream stopped");
    } catch (err) {
      console.error("Error stopping stream:", err);
      setError(err.message);
    }
  };

  // Get stream status
  const getStreamStatus = async () => {
    if (!streamId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/camera/hls/status/${streamId}`
      );
      if (response.ok) {
        const status = await response.json();
        console.log("Stream status:", status);
      }
    } catch (err) {
      console.error("Error getting stream status:", err);
    }
  };

  // Check stream status periodically
  useEffect(() => {
    if (isStreaming && streamId) {
      const interval = setInterval(getStreamStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [isStreaming, streamId]);

  // Test camera connection
  const testConnection = async () => {
    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/camera/test-connection?camera_url=${encodeURIComponent(
          cameraUrl
        )}`
      );

      if (!response.ok) {
        throw new Error(`Camera test failed: ${response.status}`);
      }

      const data = await response.json();
      alert(
        `Camera test successful!\nResponse time: ${data.response_time_seconds}s\nImage size: ${data.image_dimensions}`
      );
    } catch (err) {
      console.error("Camera test error:", err);
      setError(`Camera test failed: ${err.message}`);
    }
  };

  return (
    <div className="hls-streaming-page">
      <h1>IP Camera HLS Streaming</h1>

      <div className="controls-section">
        <div className="input-group">
          <label htmlFor="cameraUrl">Camera URL:</label>
          <input
            id="cameraUrl"
            type="text"
            value={cameraUrl}
            onChange={(e) => setCameraUrl(e.target.value)}
            placeholder="http://192.168.1.6:8080"
          />
        </div>

        <div className="button-group">
          <button onClick={testConnection} className="test-btn">
            Test Camera
          </button>
          {!isStreaming ? (
            <button onClick={startStream} className="start-btn">
              Start HLS Stream
            </button>
          ) : (
            <button onClick={stopStream} className="stop-btn">
              Stop Stream
            </button>
          )}
        </div>

        {error && <div className="error-message">Error: {error}</div>}
      </div>

      {isStreaming && streamUrl && (
        <div className="streaming-section">
          <h2>Live Stream</h2>
          <HLSPlayer
            streamUrl={streamUrl}
            autoPlay={true}
            controls={true}
            width="100%"
            height="480px"
          />
          <div className="stream-info">
            <p>Stream ID: {streamId}</p>
            <p>
              Stream URL: <code>{streamUrl}</code>
            </p>
          </div>
        </div>
      )}

      <div className="instructions">
        <h3>Instructions:</h3>
        <ol>
          <li>Enter your IP camera URL (e.g., http://192.168.1.6:8080)</li>
          <li>Click "Test Camera" to verify connection</li>
          <li>Click "Start HLS Stream" to begin streaming</li>
          <li>The HLS player will automatically load and play the stream</li>
          <li>Use "Stop Stream" to end the streaming session</li>
        </ol>
      </div>

      <style jsx>{`
        .hls-streaming-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }

        .controls-section {
          background: #f5f5f5;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .input-group {
          margin-bottom: 15px;
        }

        .input-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }

        .input-group input {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .button-group {
          display: flex;
          gap: 10px;
          margin-bottom: 15px;
        }

        button {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .test-btn {
          background: #007bff;
          color: white;
        }

        .start-btn {
          background: #28a745;
          color: white;
        }

        .stop-btn {
          background: #dc3545;
          color: white;
        }

        .error-message {
          color: #dc3545;
          background: #f8d7da;
          padding: 10px;
          border-radius: 4px;
          margin-top: 10px;
        }

        .streaming-section {
          margin-top: 20px;
        }

        .stream-info {
          margin-top: 15px;
          padding: 15px;
          background: #e9ecef;
          border-radius: 4px;
        }

        .stream-info code {
          background: #fff;
          padding: 2px 4px;
          border-radius: 3px;
          font-size: 12px;
        }

        .instructions {
          margin-top: 30px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .instructions h3 {
          margin-top: 0;
          color: #495057;
        }

        .instructions ol {
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
};

export default HLSStreamingPage;
