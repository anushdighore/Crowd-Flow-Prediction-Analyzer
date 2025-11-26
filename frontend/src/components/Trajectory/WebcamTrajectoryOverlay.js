import React, { useEffect, useRef, useState } from "react";

const getColorForId = (id) => {
  const numericId =
    typeof id === "number"
      ? id
      : parseInt(String(id).replace(/\D/g, ""), 10) || 0;
  const hue = (numericId * 47) % 360;
  return `hsl(${hue}, 85%, 55%)`;
};

const drawTrajectory = (ctx, points, color) => {
  if (!points || points.length < 2) return;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.globalAlpha = 0.85;
  ctx.beginPath();
  const [firstX, firstY] = points[0];
  ctx.moveTo(firstX, firstY);
  for (let i = 1; i < points.length; i += 1) {
    const [x, y] = points[i];
    ctx.lineTo(x, y);
  }
  ctx.stroke();

  ctx.globalAlpha = 1;
  const [lastX, lastY] = points[points.length - 1];
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
  ctx.fill();

  // Label start (A) and end (B)
  ctx.font = "12px Inter, sans-serif";
  ctx.textBaseline = "bottom";
  ctx.fillText("B", lastX + 4, lastY - 4);
  ctx.fillText("A", firstX + 4, firstY - 4);
};

const WebcamTrajectoryOverlay = ({ videoRef, tracks = [] }) => {
  const canvasRef = useRef(null);
  const [videoSize, setVideoSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const video = videoRef?.current;
    if (!video) return undefined;

    const updateSize = () => {
      if (!video.videoWidth || !video.videoHeight) return;
      setVideoSize({ width: video.videoWidth, height: video.videoHeight });
    };

    updateSize();
    video.addEventListener("loadedmetadata", updateSize);
    return () => {
      video.removeEventListener("loadedmetadata", updateSize);
    };
  }, [videoRef]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const { width, height } = videoSize;
    if (!canvas || !width || !height) {
      console.log("🎨 Canvas not ready:", { canvas: !!canvas, width, height });
      return;
    }
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    console.log("🎨 Drawing trajectories:", {
      numTracks: tracks.length,
      canvasSize: { width, height },
    });

    tracks.forEach((track) => {
      const trajectory = track?.trajectory;
      if (!Array.isArray(trajectory) || trajectory.length < 2) {
        console.log(
          `  Track ${track?.id}: skipped (trajectory length=${
            trajectory?.length || 0
          })`
        );
        return;
      }
      console.log(`  Track ${track?.id}: drawing ${trajectory.length} points`);
      drawTrajectory(
        ctx,
        trajectory,
        getColorForId(track?.id ?? track?.track_id ?? 0)
      );
    });
  }, [tracks, videoSize]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    />
  );
};

export default WebcamTrajectoryOverlay;
