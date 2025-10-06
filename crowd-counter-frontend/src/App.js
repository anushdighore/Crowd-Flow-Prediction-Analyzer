import React, { useMemo, useState } from "react";
import "./App.css";
import WebcamCounter from "./WebcamCounter";
import CSRNetUploader from "./models/CSRNetUploader";
import VMambaUploader from "./models/VMambaUploader";
import MCNNUploader from "./models/MCNNUploader";
import YOLOUploader from "./models/YOLOUploader";

function App() {
  const [mode, setMode] = useState("upload"); // "upload" or "webcam"
  const modelOptions = useMemo(
    () => [
      {
        id: "CSRNet",
        label: "CSRNet",
        description: "Density-map baseline trained for ShanghaiTech",
        ready: true,
        badge: "Production",
      },
      {
        id: "VMamba",
        label: "VMamba TMTB",
        description: "Fine-tuned best checkpoint on ShanghaiTech Part A",
        ready: true,
        badge: "Best Accuracy",
      },
      {
        id: "MCNN",
        label: "MCNN",
        description: "Legacy multi-column CNN (coming soon)",
        ready: false,
        badge: "Roadmap",
      },
      {
        id: "YOLOv8",
        label: "YOLOv8",
        description: "One-stage detector integration (coming soon)",
        ready: false,
        badge: "Roadmap",
      },
    ],
    []
  );

  const [selectedModel, setSelectedModel] = useState(
    modelOptions.find((option) => option.ready)?.id || "CSRNet"
  );

  const activeModel = useMemo(
    () => modelOptions.find((option) => option.id === selectedModel),
    [modelOptions, selectedModel]
  );

  return (
    <div className="App">
      <header className="app-header">
        <h1>🧠 VMamba-TMTB Crowd Counter</h1>
        <p>Advanced crowd counting using Visual State Space Models</p>
        <div className="mode-selector">
          <button
            className={`mode-btn ${mode === "upload" ? "active" : ""}`}
            onClick={() => setMode("upload")}
          >
            📤 Upload Image
          </button>
          <button
            className={`mode-btn ${mode === "webcam" ? "active" : ""}`}
            onClick={() => setMode("webcam")}
          >
            🎥 Live Webcam
          </button>
        </div>
      </header>

      <main className="app-main">
        {mode === "webcam" ? (
          <WebcamCounter />
        ) : (
          <>
            <section className="model-toggle-section">
              <h2 className="model-toggle-title">
                Choose Your Inference Model
              </h2>
              <p className="model-toggle-subtitle">
                Switch between production-ready CSRNet and the fine-tuned
                VMamba-TMTB best checkpoint. Upcoming research models are listed
                for visibility but remain disabled here.
              </p>

              <div className="model-toggle-grid">
                {modelOptions.map((option) => {
                  const isActive = option.id === selectedModel;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      className={`model-chip ${isActive ? "active" : ""} ${
                        option.ready ? "" : "disabled"
                      }`}
                      onClick={() =>
                        option.ready && setSelectedModel(option.id)
                      }
                      disabled={!option.ready}
                    >
                      <span className="model-chip-header">
                        <span className="model-chip-label">{option.label}</span>
                        <span
                          className={`model-chip-badge ${
                            option.ready ? "" : "badge-muted"
                          }`}
                        >
                          {option.badge}
                        </span>
                      </span>
                      <span className="model-chip-description">
                        {option.description}
                      </span>
                      {!option.ready && (
                        <span className="model-chip-coming">Coming soon</span>
                      )}
                    </button>
                  );
                })}
              </div>

              {activeModel && (
                <div className="model-context-card">
                  <h3>
                    {activeModel.label}
                    {activeModel.ready && (
                      <span className="model-context-pill">Ready</span>
                    )}
                  </h3>
                  <p>{activeModel.description}</p>
                  {activeModel.id === "VMamba" && (
                    <ul className="model-context-list">
                      <li>
                        Uses <strong>vmamba_shanghai_best.pth</strong>{" "}
                        fine-tuned on ShanghaiTech Part A.
                      </li>
                      <li>Supports high-resolution uploads (up to 10MB).</li>
                      <li>
                        Returns density-map timing breakdown and optional
                        heatmap overlay for visual analysis.
                      </li>
                    </ul>
                  )}
                  {activeModel.id === "CSRNet" && (
                    <ul className="model-context-list">
                      <li>
                        Original density regression pipeline with ImageNet
                        normalization.
                      </li>
                      <li>
                        API contract preserved; response still exposes{" "}
                        <code>count</code>.
                      </li>
                      <li>Ideal when reproducing baseline benchmarks.</li>
                    </ul>
                  )}
                </div>
              )}
            </section>

            {/* Render the selected model's uploader */}
            {selectedModel === "CSRNet" && <CSRNetUploader />}
            {selectedModel === "VMamba" && <VMambaUploader />}
            {selectedModel === "MCNN" && <MCNNUploader />}
            {selectedModel === "YOLOv8" && <YOLOUploader />}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by VMamba-TMTB | Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
