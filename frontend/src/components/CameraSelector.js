// frontend/src/components/CameraSelector.js
import React, { useState, useEffect } from "react";

const CameraSelector = ({ onSelectCamera }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState("");

  useEffect(() => {
    const getDevices = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        const deviceList = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = deviceList.filter(
          (device) => device.kind === "videoinput"
        );
        setDevices(videoDevices);
        if (videoDevices.length > 0) {
          setSelectedDevice(videoDevices[0].deviceId);
          onSelectCamera(videoDevices[0].deviceId);
        }
        // Stop the stream as we just needed it to get device list
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        console.error("Error accessing camera devices:", err);
      }
    };

    getDevices();
  }, [onSelectCamera]);

  const handleDeviceChange = (e) => {
    const deviceId = e.target.value;
    setSelectedDevice(deviceId);
    onSelectCamera(deviceId);
  };

  return (
    <div className="camera-selector">
      <label htmlFor="camera-select">Select Camera: </label>
      <select
        id="camera-select"
        value={selectedDevice}
        onChange={handleDeviceChange}
        className="camera-dropdown"
      >
        {devices.map((device) => (
          <option key={device.deviceId} value={device.deviceId}>
            {device.label || `Camera ${device.deviceId.substring(0, 5)}`}
          </option>
        ))}
      </select>
    </div>
  );
};

export default CameraSelector;
