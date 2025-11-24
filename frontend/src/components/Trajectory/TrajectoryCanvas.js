import React, { useRef, useEffect, useCallback } from "react";
import PropTypes from "prop-types";

/**
 * TrajectoryCanvas Component
 *
 * A reusable component for drawing object trajectories with state-based coloring.
 * Displays track paths, track IDs, and trajectory history points on a transparent canvas overlay.
 *
 * @param {Object} props
 * @param {React.RefObject} props.sourceRef - Reference to video or image element to match dimensions
 * @param {Object} props.results - Results object containing tracking data with tracks array
 * @param {boolean} props.enableTracking - Whether to enable trajectory drawing
 * @param {string} props.className - Optional CSS class name for the canvas
 */
const TrajectoryCanvas = ({
  sourceRef,
  results,
  enableTracking,
  className = "trajectory-overlay",
}) => {
  const canvasRef = useRef(null);

  /**
   * Draw trajectories on the canvas
   * State-based coloring:
   * - 0 (NEW): Red - newly detected track
   * - 1 (TRACKED): Green - actively tracked object
   * - 2 (LOST): Yellow - track temporarily lost
   */
  const drawTrajectories = useCallback(() => {
    console.log("🖌️ drawTrajectories called:", {
      hasCanvas: !!canvasRef.current,
      hasSource: !!sourceRef.current,
      enableTracking,
      hasResults: !!results,
      hasTracks: !!results?.tracks,
      trackCount: results?.tracks?.length || 0,
    });

    if (
      !canvasRef.current ||
      !sourceRef.current ||
      !enableTracking ||
      !results ||
      !results.tracks
    ) {
      console.log("❌ Early return from drawTrajectories");
      return;
    }

    console.log("✅ Starting to draw", results.tracks.length, "trajectories");

    const canvas = canvasRef.current;
    const source = sourceRef.current;
    const ctx = canvas.getContext("2d");

    // Match canvas size to source dimensions
    let sourceWidth, sourceHeight;
    if (source.tagName === "VIDEO") {
      sourceWidth = source.videoWidth;
      sourceHeight = source.videoHeight;
    } else if (source.tagName === "IMG") {
      sourceWidth = source.naturalWidth || source.width;
      sourceHeight = source.naturalHeight || source.height;
    } else {
      // Fallback to element dimensions
      sourceWidth = source.width;
      sourceHeight = source.height;
    }

    if (canvas.width !== sourceWidth || canvas.height !== sourceHeight) {
      canvas.width = sourceWidth;
      canvas.height = sourceHeight;
    }

    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // State-based color mapping
    const stateColors = {
      0: "#ff0000", // NEW - red
      1: "#00ff00", // TRACKED - green
      2: "#ffff00", // LOST - yellow
    };

    // Draw each track
    results.tracks.forEach((track) => {
      const color = stateColors[track.state] || "#ffffff";

      // Draw trajectory path
      if (track.trajectory && track.trajectory.length > 1) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();

        track.trajectory.forEach((point, i) => {
          const x = point[0]; // Tuple format: [x, y]
          const y = point[1];

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });

        ctx.stroke();

        // Draw small dots on trajectory points
        track.trajectory.forEach((point) => {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(point[0], point[1], 2, 0, 2 * Math.PI);
          ctx.fill();
        });
      }

      // Draw track ID label
      if (track.position && track.position.length >= 2) {
        const x = track.position[0];
        const y = track.position[1];

        // Draw text with outline for better visibility
        ctx.fillStyle = "white";
        ctx.strokeStyle = "black";
        ctx.lineWidth = 3;
        ctx.font = "bold 16px Arial";
        ctx.strokeText(`#${track.id}`, x, y - 10);
        ctx.fillText(`#${track.id}`, x, y - 10);
      }
    });
  }, [sourceRef, results, enableTracking]);

  // Redraw trajectories when results change
  useEffect(() => {
    console.log("🎨 TrajectoryCanvas useEffect:", {
      enableTracking,
      hasResults: !!results,
      hasTracks: !!results?.tracks,
      trackCount: results?.tracks?.length || 0,
      canvasRef: canvasRef.current,
      sourceRef: sourceRef.current,
    });

    if (enableTracking && results && results.tracks) {
      console.log(
        "✅ Drawing trajectories for",
        results.tracks.length,
        "tracks"
      );
      drawTrajectories();
    } else {
      console.log("❌ Not drawing trajectories:", {
        enableTracking,
        hasResults: !!results,
        hasTracks: !!results?.tracks,
      });
    }
  }, [enableTracking, results, drawTrajectories]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        pointerEvents: "none",
        zIndex: 10,
      }}
    />
  );
};

TrajectoryCanvas.propTypes = {
  sourceRef: PropTypes.shape({ current: PropTypes.instanceOf(Element) })
    .isRequired,
  results: PropTypes.shape({
    tracks: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number.isRequired,
        state: PropTypes.number,
        position: PropTypes.arrayOf(PropTypes.number),
        trajectory: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
        speed: PropTypes.number,
        frames_tracked: PropTypes.number,
      })
    ),
  }),
  enableTracking: PropTypes.bool.isRequired,
  className: PropTypes.string,
};

export default TrajectoryCanvas;
