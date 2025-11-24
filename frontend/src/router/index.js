import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LandingPage from "../pages/LandingPage/LandingPage";
import Dashboard from "../pages/Dashboard/Dashboard";
import LoginPage from "../pages/Login/LoginPage";
import WebcamPage from "../pages/webcam/Webcam";
import ExternalCameraPage from "../pages/ExternalCamera/ExternalCamera";
import ImagePage from "../pages/StaticTests/Image";
import VideoPage from "../pages/StaticTests/Video";
import HLSStreamingPage from "../components/Camera/HLSStreamingPage";
import PedestrianTracker from "../components/Trajectory/PedestrianTracker";
import Template2 from "../pages/template2";

export default function AppRouter() {
  const { isAuthenticated } = useAuth();

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Routes - Show if authenticated OR demo mode */}
        {isAuthenticated ? (
          <>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/webcam" element={<WebcamPage />} />
            <Route path="/image" element={<ImagePage />} />
            <Route path="/video" element={<VideoPage />} />
            <Route path="/external-camera" element={<ExternalCameraPage />} />
            <Route path="/externalcam" element={<ExternalCameraPage />} />
            <Route path="/hls" element={<HLSStreamingPage />} />
            <Route path="/pedestrian" element={<PedestrianTracker />} />
            <Route path="/template2" element={<Template2 />} />
          </>
        ) : (
          <>
            {/* Redirect to login if not authenticated */}
            <Route path="/dashboard" element={<LoginPage />} />
            <Route path="/webcam" element={<LoginPage />} />
            <Route path="/image" element={<LoginPage />} />
            <Route path="/video" element={<LoginPage />} />
            <Route path="/external-camera" element={<LoginPage />} />
            <Route path="/externalcam" element={<LoginPage />} />
            <Route path="/hls" element={<LoginPage />} />
            <Route path="/pedestrian" element={<LoginPage />} />
            <Route path="/template2" element={<LoginPage />} />
          </>
        )}

        {/* Fallback - redirect to home */}
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </Router>
  );
}
