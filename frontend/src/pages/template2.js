import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/Dashboard.css";
import { useAuth } from "../context/AuthContext";
import PedestrianTracker from "../components/Trajectory/PedestrianTracker";
import HLSStreamingPage from "../components/Camera/HLSStreamingPage";

function Template2() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [selectedModel, setSelectedModel] = useState("CSRNet");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  const features = [
    {
      id: "image",
      title: "Upload Image",
      icon: "📤",
      description:
        "Analyze crowd counts from static images using CSRNet, VMamba, or YOLOv8",
      path: "/image",
      color: "#667eea",
    },
    {
      id: "video",
      title: "Upload Video",
      icon: "🎬",
      description:
        "Process pre-recorded videos with real-time object detection and tracking",
      path: "/video",
      color: "#764ba2",
    },
    {
      id: "webcam",
      title: "Live Webcam",
      icon: "🎥",
      description:
        "Real-time crowd detection from your webcam with live heatmap visualization",
      path: "/webcam",
      color: "#f093fb",
    },
    {
      id: "external",
      title: "External Camera",
      icon: "📡",
      description:
        "Connect to RTSP, HTTP, or IP camera streams for remote monitoring",
      path: "/external-camera",
      color: "#4facfe",
    },
    {
      id: "hls",
      title: "HLS Streaming",
      icon: "📺",
      description:
        "Stream and analyze HLS video feeds with adaptive bitrate support",
      path: "/hls",
      color: "#43e97b",
    },
    {
      id: "pedestrian",
      title: "Pedestrian Tracking",
      icon: "👥",
      description:
        "Advanced trajectory analysis and movement pattern detection",
      path: "/pedestrian",
      color: "#fa709a",
    },
  ];

  if (!isAuthenticated) {
    return (
      <div className="not-authenticated">
        <p>Please log in to access the dashboard</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div
      className="dashboard"
      style={{
        display: "flex",
        width: "100%",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* Main Content */}
      <main
        className="dashboard-main"
        style={{
          flex: 1,
          overflowY: "auto",
          paddingRight: sidebarOpen ? "320px" : "50px",
          transition: "all 0.3s ease",
        }}
      >
        <header
          className="app-header"
          style={{
            textAlign: "center",
            marginBottom: "3rem",
            padding: "2rem 2rem 0 2rem",
          }}
        >
          <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
            🧠 Crowd Analysis Dashboard
          </h1>
          <p style={{ color: "#666", fontSize: "1.1rem" }}>
            Advanced crowd counting and tracking using Visual State Space Models
          </p>
        </header>

        <section className="features-overview" style={{ padding: "0 2rem" }}>
          <h2
            style={{
              fontSize: "1.5rem",
              marginBottom: "1.5rem",
              color: "#333",
            }}
          >
            All Features
          </h2>
          <div
            className="dashboard-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "1.5rem",
            }}
          >
            {features.map((feature) => (
              <Link
                key={feature.id}
                to={feature.path}
                className="dashboard-feature-card"
                style={{
                  textDecoration: "none",
                  background: "white",
                  borderRadius: "12px",
                  padding: "1.5rem",
                  border: "2px solid rgba(102, 126, 234, 0.15)",
                  transition: "all 0.3s ease",
                  cursor: "pointer",
                  display: "block",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow =
                    "0 8px 24px rgba(0,0,0,0.12)";
                  e.currentTarget.style.borderColor = feature.color;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                  e.currentTarget.style.borderColor =
                    "rgba(102, 126, 234, 0.15)";
                }}
              >
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
                  {feature.icon}
                </div>
                <h3
                  style={{
                    fontSize: "1.25rem",
                    marginBottom: "0.5rem",
                    color: "#333",
                  }}
                >
                  {feature.title}
                </h3>
                <p style={{ color: "#666", lineHeight: "1.6", margin: 0 }}>
                  {feature.description}
                </p>
              </Link>
            ))}
          </div>
        </section>

        <section
          className="dashboard-info"
          style={{
            marginTop: "3rem",
            padding: "2rem",
            background: "#f8f9fa",
            borderRadius: "12px",
            margin: "3rem 2rem 2rem 2rem",
          }}
        >
          <h2
            style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#333" }}
          >
            Available Models
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "1rem",
            }}
          >
            <div
              style={{
                padding: "1rem",
                background: "white",
                borderRadius: "8px",
              }}
            >
              <strong style={{ color: "#667eea" }}>CSRNet</strong>
              <p
                style={{
                  margin: "0.5rem 0 0 0",
                  fontSize: "0.9rem",
                  color: "#666",
                }}
              >
                Density-map baseline for accurate crowd estimation
              </p>
            </div>
            <div
              style={{
                padding: "1rem",
                background: "white",
                borderRadius: "8px",
              }}
            >
              <strong style={{ color: "#764ba2" }}>VMamba TMTB</strong>
              <p
                style={{
                  margin: "0.5rem 0 0 0",
                  fontSize: "0.9rem",
                  color: "#666",
                }}
              >
                Fine-tuned Visual State Space Model with best accuracy
              </p>
            </div>
            <div
              style={{
                padding: "1rem",
                background: "white",
                borderRadius: "8px",
              }}
            >
              <strong style={{ color: "#f093fb" }}>YOLOv8</strong>
              <p
                style={{
                  margin: "0.5rem 0 0 0",
                  fontSize: "0.9rem",
                  color: "#666",
                }}
              >
                Real-time detection with tracking capabilities
              </p>
            </div>
            <div
              style={{
                padding: "1rem",
                background: "white",
                borderRadius: "8px",
                opacity: 0.6,
              }}
            >
              <strong style={{ color: "#999" }}>MCNN</strong>
              <p
                style={{
                  margin: "0.5rem 0 0 0",
                  fontSize: "0.9rem",
                  color: "#666",
                }}
              >
                Multi-column CNN (Coming Soon)
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Template2;
