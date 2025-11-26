import React, {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
} from "react";
import { buildWsUrl } from "../config/api";

const WebcamContext = createContext();

export const WebcamProvider = ({ children }) => {
  // State Management
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedModel, setSelectedModel] = useState("CSRNet");
  const [enableTracking, setEnableTracking] = useState(false);
  const [enableHeatmap, setEnableHeatmap] = useState(true);
  const [detectionThreshold, setDetectionThreshold] = useState(0.5);
  const [status, setStatus] = useState("Ready");
  const [count, setCount] = useState(0);
  const [fps, setFps] = useState(0);
  const [inferenceTime, setInferenceTime] = useState(0);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
    yoloVersion: "nano",
  });

  // Results state for full backend response
  const [results, setResults] = useState(null);
  const [heatmapImage, setHeatmapImage] = useState(null);
  const [annotatedFrame, setAnnotatedFrame] = useState(null); // ML-processed frame with trajectories
  const [densityStats, setDensityStats] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [notification, setNotification] = useState(null);

  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // ✅ FIX: Removed useCallback - refs are stable, no need for memoization
  // This prevents React effect dependency issues causing premature cleanup
  const stopEverything = () => {
    console.log("🧹 Cleanup...");

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (closeError) {
        console.warn("⚠️ Error while closing WebSocket", closeError);
      }
      wsRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setMetricsHistory([]);
  };

  const connectWebSocket = () => {
    const websocketUrl = buildWsUrl("/ws/count");
    return new Promise((resolve, reject) => {
      console.log("🔌 Connecting to WebSocket at", websocketUrl);

      const ws = new WebSocket(websocketUrl);

      // Connection timeout
      const timeout = setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          ws.close();
          reject(
            new Error(
              `WebSocket connection timeout - attempted ${websocketUrl}. Is the backend up?`
            )
          );
        }
      }, 5000);

      ws.onopen = () => {
        clearTimeout(timeout);
        console.log("✅ WebSocket connected");
        setStatus("WebSocket connected");
        wsRef.current = ws;
        setNotification({
          type: "success",
          message: "WebSocket connected",
          ts: Date.now(),
        });
        resolve(ws);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("📨 Received from backend:", data);
          console.log(
            "🔥 Heatmap in response?",
            data.heatmap ? "YES ✅" : "NO ❌"
          );
          console.log("🔥 enableHeatmap state:", enableHeatmap);

          if (data.success) {
            setCount(Number(data.count ?? 0));
            setFps(data.fps || 0);
            setInferenceTime(data.inference_time_ms || 0);
            setResults(data);
            setMetricsHistory((prev) => {
              const nextPoint = {
                timestamp: Date.now(),
                count: Math.round(data.count || 0),
                fps: Number(data.fps || 0),
                inference: Number(data.inference_time_ms || 0),
              };
              const updated = [...prev, nextPoint];
              return updated.slice(-30);
            });

            // Always set heatmap if it exists in the response
            if (data.heatmap) {
              console.log(
                "🔥 Setting heatmap image, length:",
                data.heatmap.length
              );
              setHeatmapImage(data.heatmap);
            } else {
              console.log("⚠️ No heatmap in backend response");
            }

            // Set annotated frame with trajectories (from ML layer)
            if (data.annotated_frame) {
              console.log("🎨 Setting annotated frame with trajectories");
              setAnnotatedFrame(data.annotated_frame);
            }

            if (data.density_map_stats) {
              setDensityStats(data.density_map_stats);
            }

            setStatus(
              `Processing - Count: ${Math.round(data.count || 0)} | ` +
                `FPS: ${data.fps?.toFixed(1) || 0} | ` +
                `Inference: ${Number(data.inference_time_ms || 0).toFixed(0)}ms`
            );
            setError(null);
          } else {
            console.error("⚠️ Backend error:", data.error);
            setError(data.error || "Processing failed");
            setNotification({
              type: "danger",
              message: `Backend Error: ${data.error || "Processing failed"}`,
              ts: Date.now(),
            });
          }
        } catch (err) {
          console.error("❌ Error parsing WebSocket message:", err);
          setError(`Parse error: ${err.message}`);
        }
      };

      ws.onerror = (event) => {
        clearTimeout(timeout);
        console.error("❌ WebSocket error event:", event);
        const errorMsg =
          "WebSocket connection failed - ensure backend is reachable at " +
          websocketUrl;
        setError(errorMsg);
        setNotification({
          type: "danger",
          message: `WebSocket Error: ${errorMsg}`,
          ts: Date.now(),
        });

        reject(new Error(errorMsg));
      };

      ws.onclose = (event) => {
        clearTimeout(timeout);
        console.log(
          "🔌 WebSocket disconnected. Code:",
          event.code,
          "Reason:",
          event.reason
        );
        setStatus("WebSocket disconnected");

        if (!event.wasClean) {
          console.error("⚠️ WebSocket closed unexpectedly");
          setNotification({
            type: "warning",
            message: `WebSocket disconnected unexpectedly (Code: ${event.code})`,
            ts: Date.now(),
          });
        } else {
          setNotification({
            type: "success",
            message: "WebSocket disconnected cleanly",
            ts: Date.now(),
          });
        }
      };
    });
  };

  const startWebcam = async () => {
    try {
      setStatus("Requesting webcam...");
      console.log("📹 Requesting webcam access");

      // Map resolution setting to video constraints
      const resolutionMap = {
        low: { width: 320, height: 240 },
        medium: { width: 640, height: 480 },
        high: { width: 1280, height: 720 },
      };
      const videoConstraints =
        resolutionMap[settings.resolution] || resolutionMap.medium;
      console.log(
        `📹 Using resolution: ${settings.resolution} (${videoConstraints.width}x${videoConstraints.height})`
      );

      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;

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
    if (!videoRef.current || !canvasRef.current || !wsRef.current) {
      console.warn("⚠️ Missing refs or WebSocket not connected");
      return;
    }

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn("⚠️ WebSocket not open, state:", wsRef.current.readyState);
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const base64Data = canvas.toDataURL("image/jpeg", 0.8);

      const toBackendModel = (name, s) => {
        const n = (name || "").toLowerCase();
        if (n.includes("yolo")) {
          const v = (s?.yoloVersion || "nano").toLowerCase();
          if (v === "nano") return "yolo-nano";
          if (v === "small") return "yolo-small";
          if (v === "medium") return "yolo-medium";
          if (v === "large") return "yolo-large";
          if (v === "xlarge") return "yolo-xlarge";
          return "yolo";
        }
        if (n.includes("vmamba") || n.includes("tmtb")) return "tmtb";
        return "csrnet";
      };

      const payload = {
        frame: base64Data,
        model: toBackendModel(selectedModel, settings),
        tracking: enableTracking,
        heatmap: enableHeatmap,
        threshold: detectionThreshold,
      };

      wsRef.current.send(JSON.stringify(payload));
    } catch (err) {
      console.error("❌ Capture error:", err);
      setError(`Capture failed: ${err.message}`);
    }
  };

  const handleStartStreaming = async () => {
    console.log("🚀 START CLICKED - handleStartStreaming called");
    console.log("📊 Current state - isStreaming:", isStreaming);
    setError(null);

    try {
      setStatus("Starting webcam...");
      console.log("📹 Step 1: Calling startWebcam()...");
      const webcamOk = await startWebcam();
      console.log("📹 Step 1 result: webcamOk =", webcamOk);
      if (!webcamOk) {
        console.error("❌ Failed to start webcam");
        setError("Failed to start webcam");
        return;
      }

      setStatus("Connecting to backend...");
      console.log("🔌 Step 2: Connecting to WebSocket...");
      await connectWebSocket();
      console.log("🔌 Step 2: WebSocket connected");

      console.log("⏳ Step 3: Waiting for video to stabilize...");
      await new Promise((resolve) => setTimeout(resolve, 500));
      console.log("⏳ Step 3: Video stabilized");

      console.log("📤 Step 4: Starting frame capture loop (WebSocket, 10 FPS)");
      setStatus("Streaming...");
      intervalRef.current = setInterval(captureAndSend, 100);
      setIsStreaming(true);
      console.log("✅ Streaming started - isStreaming set to true");
    } catch (err) {
      console.error("❌ Start streaming error:", err);
      const errorMessage =
        err?.message || err?.toString() || "Unknown error occurred";
      setError(`Failed to start: ${errorMessage}`);
      setStatus("Failed to start");
      stopEverything();
    }
  };

  const handleStopStreaming = () => {
    console.log("⏹️ STOP CLICKED");
    stopEverything();
    setIsStreaming(false);
    setStatus("Stopped");
    setCount(0);
    setFps(0);
    setInferenceTime(0);
    setResults(null);
    setHeatmapImage(null);
    setDensityStats(null);
    console.log("✅ Stopped");

    setNotification({
      type: "info",
      message: "Streaming stopped successfully",
      ts: Date.now(),
    });
  };

  const value = {
    // State
    isStreaming,
    selectedModel,
    enableTracking,
    enableHeatmap,
    detectionThreshold,
    status,
    count,
    fps,
    inferenceTime,
    error,
    settings,
    results,
    heatmapImage,
    annotatedFrame, // ML-processed frame with bounding boxes & trajectories
    densityStats,
    metricsHistory,
    notification,

    // Refs
    videoRef,
    canvasRef,
    streamRef,
    wsRef,

    // Setters
    setSelectedModel,
    setEnableTracking,
    setEnableHeatmap,
    setDetectionThreshold,
    setSettings,

    // Actions
    handleStartStreaming,
    handleStopStreaming,
    stopEverything,
  };

  return (
    <WebcamContext.Provider value={value}>{children}</WebcamContext.Provider>
  );
};

export const useWebcam = () => {
  const context = useContext(WebcamContext);
  if (!context) {
    throw new Error("useWebcam must be used within WebcamProvider");
  }
  return context;
};
