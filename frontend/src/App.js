import React, { useMemo, useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  Link,
} from "react-router-dom";
import "./styles/App.css";
import "./styles/PageLayout.css";

// Page Components
import Webcam from "./pages/webcam/Webcam";
import Image from "./pages/StaticTests/Image";
import Video from "./pages/StaticTests/Video";
import Template from "./pages/Template";
import Template2 from "./pages/template2";
import Dashboard from "./pages/Dashboard/Dashboard";
import ExternalCameraPage from "./pages/ExternalCamera/ExternalCamera";
import CSRNetUploader from "./components/Models/CSRNet/CSRNetUploader";
import VMambaUploader from "./components/Models/TMTB/VMambaUploader";
import MCNNUploader from "./components/Models/MCNN/MCNNUploader";
import YOLOUploader from "./components/Models/YOLO/YOLOUploader";
import VideoUploader from "./components/Models/YOLO/VideoUploader";
import PedestrianTracker from "./components/Trajectory/PedestrianTracker";
import HLSStreamingPage from "./components/Camera/HLSStreamingPage";
import LoginPage from "./pages/Login/LoginPage";
import Layout from "./components/Layout/Layout";
import { useAuth } from "./context/AuthContext";

function AppContent() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

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
        description:
          "Real-time object detection for crowd counting with tracking",
        ready: true,
        badge: "Production",
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

  // Authentication check
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Only show the model selection UI on the home page
  const isHomePage = location.pathname === "/";

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route
        path="/"
        element={
          <Layout>
            {isHomePage && (
              <>
                {/* Features Section with Quick Links */}
                <section className="features-section">
                  <h2 className="features-title">Quick Access</h2>
                  <div className="features-grid">
                    <Link to="/image" className="feature-card">
                      <div className="feature-icon">📤</div>
                      <h3>Upload Image</h3>
                      <p>Analyze crowd counts from static images</p>
                    </Link>
                    <Link to="/webcam" className="feature-card">
                      <div className="feature-icon">🎥</div>
                      <h3>Live Webcam</h3>
                      <p>Real-time crowd detection from your webcam</p>
                    </Link>
                    <Link to="/external-camera" className="feature-card">
                      <div className="feature-icon">📡</div>
                      <h3>External Camera</h3>
                      <p>Connect to external camera streams</p>
                    </Link>
                    <Link to="/video" className="feature-card">
                      <div className="feature-icon">🎬</div>
                      <h3>Video Upload</h3>
                      <p>Analyze pre-recorded video files</p>
                    </Link>
                    <Link to="/dashboard" className="feature-card">
                      <div className="feature-icon">📊</div>
                      <h3>Dashboard</h3>
                      <p>View all features and system overview</p>
                    </Link>
                  </div>
                </section>

                {/* Model Selection Section */}
                <section className="model-toggle-section">
                  <h2 className="model-toggle-title">
                    Choose Your Inference Model
                  </h2>
                  <p className="model-toggle-subtitle">
                    Switch between production-ready CSRNet and the fine-tuned
                    VMamba-TMTB best checkpoint. Upcoming research models are
                    listed for visibility but remain disabled here.
                  </p>

                  <div className="model-toggle-grid">
                    {modelOptions.map((option) => (
                      <button
                        key={option.id}
                        type="button"
                        className={`model-chip ${
                          selectedModel === option.id ? "active" : ""
                        } ${option.ready ? "" : "disabled"}`}
                        onClick={() =>
                          option.ready && setSelectedModel(option.id)
                        }
                        disabled={!option.ready}
                      >
                        <span className="model-chip-header">
                          <span className="model-chip-label">
                            {option.label}
                          </span>
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
                    ))}
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
                          <li>
                            Supports high-resolution uploads (up to 10MB).
                          </li>
                          <li>
                            Returns density-map timing breakdown and optional
                            heatmap overlay for visual analysis.
                          </li>
                        </ul>
                      )}
                      {activeModel.id === "YOLOv8" && (
                        <ul className="model-context-list">
                          <li>
                            Real-time object detection for crowd counting with
                            support for 5 model sizes.
                          </li>
                          <li>
                            Choose from Nano (fastest) to XLarge (most accurate)
                            based on your needs.
                          </li>
                          <li>
                            Supports advanced tracking and per-frame speed
                            analytics (Phase 2).
                          </li>
                          <li>
                            Ideal for real-time applications requiring bounding
                            box accuracy.
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
          </Layout>
        }
      />
      <Route
        path="/webcam"
        element={
          <Layout>
            <Webcam />
          </Layout>
        }
      />
      <Route
        path="/image"
        element={
          <Layout>
            <Image />
          </Layout>
        }
      />
      <Route
        path="/external-camera"
        element={
          <Layout>
            <ExternalCameraPage />
          </Layout>
        }
      />
      <Route
        path="/hls"
        element={
          <Layout>
            <HLSStreamingPage />
          </Layout>
        }
      />
      <Route
        path="/video"
        element={
          <Layout>
            <Video />
          </Layout>
        }
      />
      <Route
        path="/template"
        element={
          <Layout>
            <Template />
          </Layout>
        }
      />
      <Route
        path="/template2"
        element={
          <Layout>
            <Template2 />
          </Layout>
        }
      />
      <Route
        path="/pedestrian"
        element={
          <Layout>
            <PedestrianTracker />
          </Layout>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
