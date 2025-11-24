import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/WebcamPage.css";
import "../styles/WebcamCounterNew.css";
import { useAuth } from "../context/AuthContext";
import VideoUploader from "../components/Models/YOLO/VideoUploader";

function Template() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="webcam-page">
        <p>Please log in to access the video upload</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div className="webcam-page">
      <main className="webcam-main" style={{ width: "100%", margin: "0" }}>
        <VideoUploader />
      </main>
    </div>
  );
}

export default Template;
