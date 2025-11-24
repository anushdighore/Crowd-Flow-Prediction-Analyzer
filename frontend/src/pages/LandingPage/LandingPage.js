import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/LandingPage.css";
import { useAuth } from "../../context/AuthContext";

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage for saved preference
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) return JSON.parse(saved);
    // Check system preference
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/login");
    }
  };

  return (
    <div className={`landing-page ${isDarkMode ? "dark-mode" : ""}`}>
      {/* Navigation Bar */}
      <nav className="landing-nav">
        <div className="landing-nav-container">
          <div className="landing-logo">
            <span className="logo-icon">🧠</span>
            <span className="logo-text">Crowd Flow</span>
          </div>
          <div className="landing-nav-links">
            <nav className="main-nav">
              <button
                className="nav-link"
                onClick={() =>
                  document
                    .getElementById("features")
                    .scrollIntoView({ behavior: "smooth" })
                }
              >
                Features
              </button>
              <button
                className="nav-link"
                onClick={() =>
                  document
                    .getElementById("how-it-works")
                    .scrollIntoView({ behavior: "smooth" })
                }
              >
                How It Works
              </button>
              <button
                className="nav-link"
                onClick={() =>
                  document
                    .getElementById("contact")
                    .scrollIntoView({ behavior: "smooth" })
                }
              >
                Contact
              </button>
            </nav>
            <div className="nav-buttons">
              <button
                className="theme-toggle"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDarkMode(!isDarkMode);
                }}
                title={
                  isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"
                }
              >
                {isDarkMode ? "☀️" : "🌙"}
              </button>
              {isAuthenticated ? (
                <button
                  className="nav-link btn-primary"
                  onClick={() => navigate("/dashboard")}
                >
                  Go to Dashboard
                </button>
              ) : (
                <>
                  <button
                    className="nav-link"
                    onClick={() => navigate("/login")}
                  >
                    Sign In
                  </button>
                  <button
                    className="nav-link btn-primary"
                    onClick={() => navigate("/signup")}
                  >
                    Sign Up Free
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Image Header */}
      <section className="hero-header">
        <div className="hero-content-wrapper">
          <div className="hero-left">
            <div
              className="hero-background-blurred"
              style={{
                backgroundImage: `url('https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80')`,
              }}
            ></div>
            <div className="hero-text-overlay">
              <h1 className="hero-title">Advanced Crowd Counting & Analysis</h1>
              <p className="hero-subtitle">
                Powered by Visual State Space Models (VMamba-TMTB) and YOLO
                Real-time Detection
              </p>
              <button className="btn-get-started" onClick={handleGetStarted}>
                Get Started
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <h2>Key Features</h2>
        <div className="features-grid">
          {[
            {
              icon: "📤",
              title: "Image Upload",
              description:
                "Upload images for instant crowd density analysis using multiple AI models",
              path: "/image",
            },
            {
              icon: "🎬",
              title: "Video Processing",
              description:
                "Process video files with frame-by-frame crowd tracking and trajectory analysis",
              path: "/video",
            },
            {
              icon: "🎥",
              title: "Live Webcam",
              description:
                "Real-time crowd counting directly from your webcam with instant results",
              path: "/webcam",
            },
            {
              icon: "📡",
              title: "External Camera",
              description:
                "Connect to IP cameras and external feeds for continuous monitoring",
              path: "/external-camera",
            },
            {
              icon: "📺",
              title: "HLS Streaming",
              description:
                "Stream HLS feeds with real-time crowd density estimation",
              path: "/hls-streaming",
            },
            {
              icon: "👥",
              title: "Pedestrian Tracking",
              description:
                "Advanced trajectory tracking and pedestrian movement analysis",
              path: "/pedestrian-tracking",
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="feature-card"
              onClick={() =>
                isAuthenticated
                  ? navigate(feature.path)
                  : navigate("/login", { state: { from: feature.path } })
              }
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Models Section */}
      <section className="models">
        <h2>Available AI Models</h2>
        <div className="models-grid">
          <div className="model-card">
            <h3>🧠 VMamba-TMTB</h3>
            <p className="model-badge">Best Accuracy</p>
            <p>Fine-tuned Visual Mamba with state-space attention mechanisms</p>
          </div>
          <div className="model-card">
            <h3>📊 CSRNet</h3>
            <p className="model-badge">Production</p>
            <p>Density-map baseline trained on ShanghaiTech dataset</p>
          </div>
          <div className="model-card">
            <h3>🎯 YOLOv8</h3>
            <p className="model-badge">Production</p>
            <p>Real-time object detection with tracking capabilities</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <h2>Ready to analyze crowds?</h2>
        <button className="btn-get-started-large" onClick={handleGetStarted}>
          {isAuthenticated ? "Go to Dashboard" : "Sign In Now"}
        </button>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>&copy; 2025 Crowd Flow Prediction Analyzer. All rights reserved.</p>
      </footer>
    </div>
  );
}
