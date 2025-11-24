// frontend/src/pages/CameraPage.js
import React, { useState } from "react";
import CameraSelector from "../components/CameraSelector";
import CameraStream from "../components/CameraStream";
import "../styles/CameraPage.css";

const CameraPage = () => {
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleCameraSelect = (deviceId) => {
    setSelectedCamera(deviceId);
  };

  const handleFrameCapture = async (imageData) => {
    setCapturedImage(imageData);
    setIsProcessing(true);

    try {
      // TODO: Connect to your backend API
      // const response = await fetch('http://localhost:8000/api/process', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ image: imageData })
      // });
      // const data = await response.json();
      // setResult(data);

      // Simulate API call
      setTimeout(() => {
        setResult({
          count: Math.floor(Math.random() * 50),
          densityMap: "path/to/density_map.png",
        });
        setIsProcessing(false);
      }, 1000);
    } catch (error) {
      console.error("Error processing image:", error);
      setIsProcessing(false);
    }
  };

  return (
    <div className="camera-page">
      <h1>Camera Analysis</h1>

      <div className="camera-controls">
        <CameraSelector onSelectCamera={handleCameraSelect} />
      </div>

      <div className="camera-container">
        <div className="camera-feed-container">
          {selectedCamera ? (
            <CameraStream
              deviceId={selectedCamera}
              onFrameCapture={handleFrameCapture}
            />
          ) : (
            <div className="no-camera">No camera selected or available</div>
          )}
        </div>

        <div className="results-panel">
          <h3>Analysis Results</h3>
          {isProcessing ? (
            <div className="loading">Processing...</div>
          ) : result ? (
            <div className="results">
              <p>
                People Count: <strong>{result.count}</strong>
              </p>
              {result.densityMap && (
                <div className="density-map">
                  <img src={result.densityMap} alt="Density Map" />
                </div>
              )}
            </div>
          ) : (
            <div className="no-results">
              Capture an image to see analysis results
            </div>
          )}
        </div>
      </div>

      {capturedImage && (
        <div className="captured-image">
          <h3>Last Captured Frame</h3>
          <img src={capturedImage} alt="Captured" />
        </div>
      )}
    </div>
  );
};

export default CameraPage;
