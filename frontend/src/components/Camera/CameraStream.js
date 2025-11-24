// frontend/src/components/Camera/CameraStream.js
import React, { useRef, useEffect } from "react";

const CameraStream = ({ deviceId, onFrameCapture }) => {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    const startStream = async () => {
      try {
        // Stop any existing stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
        }

        const constraints = {
          video: {
            deviceId: deviceId ? { exact: deviceId } : undefined,
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
        }
      } catch (err) {
        console.error("Error accessing camera:", err);
      }
    };

    startStream();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [deviceId]);

  const captureFrame = () => {
    if (videoRef.current && onFrameCapture) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      onFrameCapture(canvas.toDataURL("image/jpeg"));
    }
  };

  return (
    <div className="camera-stream">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="camera-feed"
      />
      <button onClick={captureFrame} className="capture-button">
        Capture Frame
      </button>
    </div>
  );
};

export default CameraStream;
