import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "../../styles/OldHome.css";

function OldHome() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="container my-5">
      <div className="row">
        {/* Main Content */}
        <div className="col-lg-8">
          {/* Welcome Card */}
          <div className="card mb-4">
            <div className="card-body">
              <h3 className="card-title">Welcome to Crowd Analyzer</h3>
              <p className="text-muted">
                A real-time system for pedestrian detection, tracking, and
                density analytics.
              </p>
              <ul>
                <li>
                  <b>YOLO</b>: Real-time person detection and tracking
                </li>
                <li>
                  <b>CSRNet</b>: Accurate crowd density estimation
                </li>
                <li>
                  <b>OpenCV</b>: Video capture and frame processing
                </li>
                <li>
                  <b>Flask + Socket.IO</b>: Web backend and real-time updates
                </li>
                <li>
                  <b>Charts</b>: Time-series metrics and density visuals
                </li>
              </ul>
              <Link to="/old-dashboard" className="btn btn-primary">
                <i className="bi bi-speedometer2"></i> Go to Dashboard
              </Link>
            </div>
          </div>

          {/* How It Works Card */}
          <div className="card">
            <div className="card-body">
              <h5>How it works</h5>
              <ol>
                <li>
                  Choose a video source (webcam, IP Webcam app, or upload a
                  local file)
                </li>
                <li>Start analysis to see the original stream with overlays</li>
                <li>
                  View live metrics: people count, unique IDs, density, FPS
                </li>
                <li>Export recent metrics as JSON</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="col-lg-4">
          <div className="card">
            <div className="card-body">
              <h5>Project Info</h5>
              <p>
                <b>Tech Stack</b>
              </p>
              <ul className="mb-2">
                <li>Python, Flask, Socket.IO</li>
                <li>Ultralytics YOLO, OpenCV</li>
                <li>Bootstrap, Chart.js</li>
                <li>React.js Frontend</li>
              </ul>
              <p className="mb-0">
                Use the IP Webcam Android app and enter your phone IP
                (http://IP:8080/video) for a mobile camera feed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OldHome;
