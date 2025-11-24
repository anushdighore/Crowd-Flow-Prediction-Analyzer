import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/WebcamPage.css";
import "../../styles/WebcamCounterNew.css";
import { useAuth } from "../../context/AuthContext";
import VideoUploader from "../../components/Models/YOLO/VideoUploader";
import RightMenu from "../../components/Menu/RightMenu";

function Video() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [selectedModel, setSelectedModel] = useState("YOLOv8");
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  if (!isAuthenticated) {
    return (
      <div className="webcam-page">
        <p>Please log in to access the video upload</p>
        <button onClick={() => navigate("/login")}>Go to Login</button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", width: "100%" }}>
      <main
        className="webcam-main"
        style={{ flex: 1, width: "100%", margin: "0" }}
      >
        <VideoUploader />
      </main>
      <RightMenu
        isOpen={isRightMenuOpen}
        onToggle={setIsRightMenuOpen}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        settings={settings}
        onSettingsChange={setSettings}
      />
    </div>
  );
}

export default Video;
