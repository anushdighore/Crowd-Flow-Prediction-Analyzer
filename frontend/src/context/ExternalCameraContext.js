import React, {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
} from "react";

const ExternalCameraContext = createContext();

const WS_BASE = "ws://localhost:8000";

// Demo camera URLs that work with common IP camera apps
const DEMO_URLS = {
  // IP Webcam (Android) - most common
  ipWebcam: "http://192.168.1.100:8080/video",
  // DroidCam
  droidCam: "http://192.168.1.100:4747/video",
  // Demo mode - uses backend demo endpoint
  demo: "demo://local/video",
};

export const ExternalCameraProvider = ({ children }) => {
  // State Management
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [cameraUrl, setCameraUrl] = useState(DEMO_URLS.ipWebcam);
  const [demoMode, setDemoMode] = useState(false); // Demo mode flag
  const [selectedModel, setSelectedModel] = useState("CSRNet"); // Default to CSRNet
  const [enableTracking, setEnableTracking] = useState(true);
  const [enableHeatmap, setEnableHeatmap] = useState(true);
  const [detectionThreshold, setDetectionThreshold] = useState(0.5);
  const [status, setStatus] = useState("Ready");
  const [count, setCount] = useState(0);
  const [fps, setFps] = useState(0);
  const [inferenceTime, setInferenceTime] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [error, setError] = useState(null);

  // Auto-switch settings
  const [autoSwitch, setAutoSwitch] = useState(false);
  const [autoSwitchThreshold, setAutoSwitchThreshold] = useState(30);
  const [currentAutoModel, setCurrentAutoModel] = useState("yolo-nano");

  // Results state
  const [results, setResults] = useState(null);
  const [heatmapImage, setHeatmapImage] = useState(null);
  const [annotatedFrame, setAnnotatedFrame] = useState(null); // ML-processed frame with trajectories
  const [countHistory, setCountHistory] = useState([]);
  const [fpsHistory, setFpsHistory] = useState([]);
  const [notification, setNotification] = useState(null);

  // Settings
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  // Refs
  const imgRef = useRef(null);
  const heatmapRef = useRef(null);
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
  const stopEverything = useCallback(() => {
    console.log("🧹 External Camera Cleanup...");
    setIsStreaming(false);
    setResults(null);
    setFps(0);
    setFrameCount(0);
    setAnnotatedFrame(null);
    setHeatmapImage(null);
    disconnectWebSocket();
    setStatus("Stopped");
    setNotification({
      type: "info",
      message: "External camera stream stopped",
      ts: Date.now(),
    });
  }, [disconnectWebSocket]);

  // Request frame from backend
  const requestFrame = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "get_frame" }));
    }
  }, []);

  // Send occupancy configuration to backend
  const sendOccupancyConfig = useCallback((config) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "update_occupancy_config",
          ...config,
        })
      );
      console.log("📊 Sent occupancy config:", config);
    }
  }, []);

  // Helper function to convert UI model name to backend model name (defined early for use in connectWebSocket)
  const toBackendModelName = (name, settingsObj) => {
    const n = (name || "").toLowerCase();
    if (n.includes("yolo")) {
      const v = (settingsObj?.yoloVersion || "nano").toLowerCase();
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

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(`${WS_BASE}/ws/external-camera`);

        ws.onopen = () => {
          console.log("✅ External camera WebSocket connected");
          setError(null);
          setStatus("WebSocket connected");

          const modelToUse = autoSwitch ? currentAutoModel : selectedModel;
          const backendModel = toBackendModelName(modelToUse, settings);

          // Use demo URL if demo mode is enabled
          const urlToUse = demoMode ? "demo://local/video" : cameraUrl;

          // Get occupancy config from localStorage or use defaults
          const savedOccupancyConfig = localStorage.getItem('occupancySettings');
          const occupancyConfig = savedOccupancyConfig 
            ? JSON.parse(savedOccupancyConfig)
            : { max_capacity: 100, alert_threshold: 80, reset_threshold: 78, window_size: 3 };

          const connectionData = {
            camera_url: urlToUse,
            model: backendModel,
            tracking: enableTracking,
            heatmap: enableHeatmap,
            demo_mode: demoMode,
            occupancy_config: occupancyConfig,
          };

          console.log("📤 Sending connection data:", connectionData);
          ws.send(JSON.stringify(connectionData));

          setNotification({
            type: "success",
            message: "Connected to external camera",
            ts: Date.now(),
          });

          resolve(ws);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          if (data.success) {
            // Update frame display
            if (data.frame && imgRef.current) {
              imgRef.current.src = data.frame;
            }

            // Update heatmap display
            if (data.heatmap) {
              setHeatmapImage(data.heatmap);
              if (heatmapRef.current) {
                heatmapRef.current.src = data.heatmap;
              }
            }

            // Update annotated frame with trajectories (from ML layer)
            if (data.annotated_frame) {
              console.log("🎨 Setting annotated frame with trajectories");
              setAnnotatedFrame(data.annotated_frame);
            }

            // Update metrics
            if (data.count !== undefined) {
              setResults(data);
              setCount(data.count);
              setFps(data.fps || 0);
              setInferenceTime(data.inference_time_ms || 0);
              setFrameCount(data.frame_number || 0);

              // Track history for charts
              setCountHistory((prev) => [
                ...prev.slice(-49),
                { time: Date.now(), count: data.count },
              ]);
              setFpsHistory((prev) => [
                ...prev.slice(-49),
                { time: Date.now(), fps: data.fps || 0 },
              ]);

              // Log tracking data
              if (data.tracks) {
                console.log("🎯 Tracking data:", data.tracks.length, "tracks");
              }

              // Auto-switch logic
              if (autoSwitch) {
                const countVal = data.count;
                if (
                  countVal < autoSwitchThreshold &&
                  !currentAutoModel.startsWith("yolo")
                ) {
                  setCurrentAutoModel("yolo-nano");
                  console.log(
                    `🔄 Auto-switched to YOLO (count: ${countVal} < ${autoSwitchThreshold})`
                  );
                  if (wsRef.current?.readyState === WebSocket.OPEN) {
                    wsRef.current.send(
                      JSON.stringify({
                        camera_url: cameraUrl,
                        model: "yolo-nano",
                        tracking: enableTracking,
                      })
                    );
                  }
                } else if (
                  countVal >= autoSwitchThreshold &&
                  currentAutoModel.startsWith("yolo")
                ) {
                  setCurrentAutoModel("csrnet");
                  console.log(
                    `🔄 Auto-switched to CSRNet (count: ${countVal} >= ${autoSwitchThreshold})`
                  );
                  if (wsRef.current?.readyState === WebSocket.OPEN) {
                    wsRef.current.send(
                      JSON.stringify({
                        camera_url: cameraUrl,
                        model: "csrnet",
                        tracking: enableTracking,
                      })
                    );
                  }
                }
              }

              setStatus(
                `Processing - Count: ${Math.round(data.count)} | FPS: ${(
                  data.fps || 0
                ).toFixed(1)}`
              );
            }
          } else {
            console.error("Processing error:", data.error);
            setError(data.error);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          setError("WebSocket connection error");
          reject(error);
        };

        ws.onclose = (event) => {
          console.log("❌ External camera WebSocket disconnected");
          setStatus("Disconnected");
          if (!event.wasClean) {
            setNotification({
              type: "warning",
              message: "Connection lost unexpectedly",
              ts: Date.now(),
            });
          }
        };

        wsRef.current = ws;
      } catch (err) {
        setError(`Failed to connect: ${err.message}`);
        reject(err);
      }
    });
  }, [
    cameraUrl,
    demoMode,
    selectedModel,
    autoSwitch,
    currentAutoModel,
    enableTracking,
    enableHeatmap,
    autoSwitchThreshold,
    settings,
  ]);

  // Start streaming
  const handleStartStreaming = useCallback(async () => {
    if (!demoMode && !cameraUrl) {
      setError("Please enter a valid camera URL or enable Demo Mode");
      return;
    }

    console.log("📹 Starting external camera stream");
    console.log("   Camera URL:", demoMode ? "DEMO MODE" : cameraUrl);
    console.log("   Model:", selectedModel);
    console.log("   Demo Mode:", demoMode);

    setLoading(true);
    setError(null);
    stopEverything();

    try {
      setStatus("Connecting...");
      await connectWebSocket();

      setIsStreaming(true);
      setStatus("Streaming...");

      // Request frames at 5 FPS
      intervalRef.current = setInterval(requestFrame, 200);

      setLoading(false);
      setNotification({
        type: "success",
        message: demoMode
          ? "Demo mode streaming started"
          : "External camera streaming started",
        ts: Date.now(),
      });
    } catch (e) {
      console.error("Start stream error:", e);
      setError(e.message);
      stopEverything();
      setLoading(false);
    }
  }, [
    cameraUrl,
    demoMode,
    selectedModel,
    stopEverything,
    connectWebSocket,
    requestFrame,
  ]);

  // Stop streaming
  const handleStopStreaming = useCallback(() => {
    console.log("⏹️ Stopping external camera stream");
    stopEverything();
  }, [stopEverything]);

  // Test camera connection
  const testConnection = async () => {
    // If demo mode is enabled, skip the actual test and return success
    if (demoMode) {
      setNotification({
        type: "success",
        message: "Demo mode enabled - using local demo video",
        ts: Date.now(),
      });
      setStatus("Demo mode ready");
      return true;
    }

    try {
      setError(null);
      setStatus("Testing connection...");
      const res = await fetch(
        `http://localhost:8000/api/camera/test-connection?camera_url=${encodeURIComponent(
          cameraUrl
        )}`
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          data.detail || data.message || "Failed to connect to camera"
        );
      }
      setNotification({
        type: "success",
        message: `Camera test successful! Response time: ${data.response_time_seconds}s`,
        ts: Date.now(),
      });
      setStatus("Connection test passed");
      return true;
    } catch (err) {
      console.error("Camera test error:", err);
      setError(`Camera test failed: ${err.message}`);
      setStatus("Connection test failed");
      return false;
    }
  };

  // Update model (and notify backend if streaming)
  const updateModel = useCallback(
    (newModel) => {
      console.log("🎯 External Camera - Model selected:", newModel);
      setSelectedModel(newModel);

      // Convert to backend model name using the helper defined above
      const backendModel = toBackendModelName(newModel, settings);
      console.log("🎯 Backend model name:", backendModel);

      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            camera_url: demoMode ? "demo://local/video" : cameraUrl,
            model: backendModel,
            tracking: enableTracking,
            heatmap: enableHeatmap,
            demo_mode: demoMode,
          })
        );
      }
    },
    [cameraUrl, enableTracking, enableHeatmap, settings, demoMode]
  );

  // Computed values
  const densityModelActive = ["csrnet", "vmamba", "tmtb"].includes(
    (selectedModel || "").toLowerCase()
  );
  const isYoloSelected = (selectedModel || "").toLowerCase().includes("yolo");
  const yoloActive =
    isYoloSelected || (results?.model || "").toLowerCase().includes("yolo");
  const hasBackendTracks =
    Array.isArray(results?.tracks) && results.tracks.length > 0;
  const trackingActive = enableTracking || hasBackendTracks;
  const trajectoryTracks = results?.tracks || [];
  const showAnnotatedFrame =
    isStreaming && yoloActive && trackingActive && annotatedFrame;

  const value = {
    // State
    isStreaming,
    loading,
    cameraUrl,
    demoMode,
    selectedModel,
    enableTracking,
    enableHeatmap,
    detectionThreshold,
    status,
    count,
    fps,
    inferenceTime,
    frameCount,
    error,
    autoSwitch,
    autoSwitchThreshold,
    currentAutoModel,
    results,
    heatmapImage,
    annotatedFrame,
    countHistory,
    fpsHistory,
    notification,
    settings,

    // Constants
    DEMO_URLS,

    // Computed
    densityModelActive,
    yoloActive,
    trackingActive,
    trajectoryTracks,
    showAnnotatedFrame,

    // Refs
    imgRef,
    heatmapRef,
    wsRef,

    // Setters
    setCameraUrl,
    setDemoMode,
    setSelectedModel: updateModel,
    setEnableTracking,
    setEnableHeatmap,
    setDetectionThreshold,
    setAutoSwitch,
    setAutoSwitchThreshold,
    setSettings,

    // Actions
    handleStartStreaming,
    handleStopStreaming,
    stopEverything,
    testConnection,
    sendOccupancyConfig,
  };

  return (
    <ExternalCameraContext.Provider value={value}>
      {children}
    </ExternalCameraContext.Provider>
  );
};

export const useExternalCamera = () => {
  const context = useContext(ExternalCameraContext);
  if (!context) {
    throw new Error(
      "useExternalCamera must be used within ExternalCameraProvider"
    );
  }
  return context;
};
