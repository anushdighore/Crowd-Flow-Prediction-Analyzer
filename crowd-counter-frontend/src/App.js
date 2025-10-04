import React, { useState } from "react";
import "./App.css";
import WebcamCounter from "./WebcamCounter";
import CSRNetUploader from "./models/CSRNetUploader";
import VMambaUploader from "./models/VMambaUploader";
import MCNNUploader from "./models/MCNNUploader";
import YOLOUploader from "./models/YOLOUploader";

function App() {
  const [mode, setMode] = useState("upload"); // "upload" or "webcam"
  const [selectedModel, setSelectedModel] = useState("CSRNet");

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
            {/* Model selection dropdown */}
            <div className="model-select-section">
              <label htmlFor="model-select" className="model-select-label">
                Select Model:
              </label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="model-select-dropdown"
              >
                <option value="CSRNet">CSRNet</option>
                <option value="VMamba">VMamba</option>
                <option value="MCNN">MCNN</option>
                <option value="YOLOv8">YOLOv8</option>
              </select>
            </div>

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
