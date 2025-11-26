import React from "react";
import { FormControlLabel, Switch } from "@mui/material";
import { useWebcam } from "../../context/WebcamContext";

const MODEL_OPTIONS = [
  { id: "CSRNet", label: "CSRNet", tagline: "Density regression" },
  { id: "VMamba", label: "TMTB / VMamba", tagline: "High fidelity" },
  { id: "YOLOv8", label: "YOLOv8", tagline: "Tracking + boxes" },
];

const isDensityModel = (model) =>
  ["csrnet", "vmamba", "tmtb"].includes((model || "").toLowerCase());

const WebcamControlPanel = () => {
  const {
    isStreaming,
    selectedModel,
    enableHeatmap,
    enableTracking,
    detectionThreshold,
    settings,
    setSelectedModel,
    setEnableHeatmap,
    setEnableTracking,
    setDetectionThreshold,
    setSettings,
    handleStartStreaming,
    handleStopStreaming,
  } = useWebcam();

  const handleStartSystem = () => {
    if (isStreaming) {
      handleStopStreaming();
    } else {
      handleStartStreaming();
    }
  };

  const handleAutoToggle = (checked) => {
    setSettings({
      ...settings,
      autoMode: checked,
    });
  };

  const handleRealtimeToggle = (checked) => {
    setSettings({
      ...settings,
      realtime: checked,
    });
  };

  const handleResolutionChange = (value) => {
    setSettings({
      ...settings,
      resolution: value,
    });
  };

  const disabledHeatmapToggle = !isDensityModel(selectedModel);

  return (
    <section
      style={{
        background: "white",
        borderRadius: "16px",
        padding: "1.75rem",
        boxShadow: "0 20px 45px rgba(15,23,42,0.08)",
        marginBottom: "2rem",
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "1rem",
        }}
      >
        <div>
          <p
            style={{
              textTransform: "uppercase",
              fontSize: "0.8rem",
              letterSpacing: "0.08em",
              margin: 0,
              color: "#94a3b8",
            }}
          >
            Control Center
          </p>
          <h2 style={{ margin: "0.3rem 0 0", fontSize: "1.75rem" }}>
            {isStreaming ? "Live system active" : "System idle"}
          </h2>
          <p style={{ margin: "0.25rem 0 0", color: "#64748b" }}>
            Manage model, automation, and capture preferences.
          </p>
        </div>
        <button
          onClick={handleStartSystem}
          style={{
            flexShrink: 0,
            padding: "0.85rem 1.75rem",
            borderRadius: "999px",
            border: "none",
            fontSize: "1rem",
            fontWeight: 600,
            cursor: "pointer",
            color: "white",
            background: isStreaming
              ? "linear-gradient(135deg,#f87171,#ef4444)"
              : "linear-gradient(135deg,#34d399,#10b981)",
            boxShadow: "0 15px 35px rgba(16,185,129,0.35)",
            transition: "transform 150ms ease",
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.97)")}
          onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          {isStreaming ? "⏹ Stop System" : "🚀 Start System"}
        </button>
      </header>

      {/* Model selector */}
      <section style={{ marginTop: "1.75rem" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "0.75rem",
          }}
        >
          <h3 style={{ margin: 0 }}>Model selector</h3>
          <FormControlLabel
            control={
              <Switch
                size="small"
                checked={settings.autoMode || false}
                onChange={(e) => handleAutoToggle(e.target.checked)}
              />
            }
            label="Auto-select"
            sx={{
              margin: 0,
              ".MuiFormControlLabel-label": {
                fontSize: "0.85rem",
                color: "#475569",
              },
            }}
          />
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "0.75rem",
          }}
        >
          {MODEL_OPTIONS.map((option) => {
            const isActive = selectedModel === option.id;
            return (
              <button
                key={option.id}
                onClick={() => setSelectedModel(option.id)}
                style={{
                  borderRadius: "12px",
                  border: isActive ? "2px solid #6366f1" : "1px solid #e2e8f0",
                  padding: "1rem",
                  textAlign: "left",
                  background: isActive ? "#eef2ff" : "white",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontWeight: 700 }}>{option.label}</div>
                <p
                  style={{
                    margin: "0.2rem 0 0",
                    color: "#64748b",
                    fontSize: "0.85rem",
                  }}
                >
                  {option.tagline}
                </p>
                {isActive && (
                  <div
                    style={{
                      marginTop: "0.5rem",
                      fontSize: "0.75rem",
                      color: "#4c1d95",
                    }}
                  >
                    Active model
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* Feature toggles */}
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
          gap: "1rem",
          marginTop: "1.75rem",
        }}
      >
        <div
          style={{
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            padding: "1rem",
            background: "#f8fafc",
          }}
        >
          <h4 style={{ marginTop: 0 }}>Heatmap overlay</h4>
          <p style={{ fontSize: "0.85rem", color: "#64748b" }}>
            Available for CSRNet/TMTB models.
          </p>
          <FormControlLabel
            control={
              <Switch
                checked={enableHeatmap && !disabledHeatmapToggle}
                onChange={(e) => setEnableHeatmap(e.target.checked)}
                disabled={disabledHeatmapToggle}
              />
            }
            label={
              disabledHeatmapToggle
                ? "Switch to density model"
                : "Show density heatmap"
            }
            sx={{
              margin: 0,
              ".MuiFormControlLabel-label": {
                fontSize: "0.85rem",
                color: "#475569",
              },
            }}
          />
        </div>

        <div
          style={{
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            padding: "1rem",
            background: "#f8fafc",
          }}
        >
          <h4 style={{ marginTop: 0 }}>Trajectory tracking</h4>
          <p style={{ fontSize: "0.85rem", color: "#64748b" }}>
            Requires YOLOv8 selection.
          </p>
          <FormControlLabel
            control={
              <Switch
                checked={enableTracking}
                onChange={(e) => setEnableTracking(e.target.checked)}
                disabled={selectedModel !== "YOLOv8"}
              />
            }
            label={
              selectedModel === "YOLOv8"
                ? "Track unique IDs"
                : "Activate YOLOv8"
            }
            sx={{
              margin: 0,
              ".MuiFormControlLabel-label": {
                fontSize: "0.85rem",
                color: "#475569",
              },
            }}
          />
        </div>

        <div
          style={{
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            padding: "1rem",
            background: "#f8fafc",
          }}
        >
          <h4 style={{ marginTop: 0 }}>Low latency mode</h4>
          <p style={{ fontSize: "0.85rem", color: "#64748b" }}>
            Drops resolution + throttles heatmap.
          </p>
          <FormControlLabel
            control={
              <Switch
                checked={settings.realtime || false}
                onChange={(e) => handleRealtimeToggle(e.target.checked)}
              />
            }
            label="Realtime throttling"
            sx={{
              margin: 0,
              ".MuiFormControlLabel-label": {
                fontSize: "0.85rem",
                color: "#475569",
              },
            }}
          />
        </div>
      </section>

      {/* Resolution + sensitivity */}
      <section
        style={{
          marginTop: "1.75rem",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1.5rem",
        }}
      >
        <div>
          <h4>Input resolution</h4>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {["low", "medium", "high"].map((quality) => {
              const active = settings.resolution === quality;
              return (
                <button
                  key={quality}
                  onClick={() => handleResolutionChange(quality)}
                  style={{
                    flex: 1,
                    padding: "0.65rem 0.5rem",
                    borderRadius: "8px",
                    border: active ? "2px solid #0ea5e9" : "1px solid #cbd5f5",
                    background: active ? "#e0f2fe" : "white",
                    textTransform: "capitalize",
                    cursor: "pointer",
                  }}
                >
                  {quality}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <h4>Detection sensitivity</h4>
          <label
            htmlFor="threshold"
            style={{ fontSize: "0.85rem", color: "#475569" }}
          >
            Confidence: {(detectionThreshold * 100).toFixed(0)}%
          </label>
          <input
            id="threshold"
            type="range"
            min="0.1"
            max="0.95"
            step="0.05"
            value={detectionThreshold}
            onChange={(e) => setDetectionThreshold(parseFloat(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>
      </section>
    </section>
  );
};

export default WebcamControlPanel;
