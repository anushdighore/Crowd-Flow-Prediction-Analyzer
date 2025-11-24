import React from "react";

/**
 * TrackingDetails Component
 * Displays active tracks table and tracking statistics
 */
function TrackingDetails({ results, enableTracking }) {
  if (!enableTracking || !results) return null;

  return (
    <>
      {results.tracks && results.tracks.length > 0 ? (
        <div className="tracking-details">
          <h3>📊 Active Tracks</h3>
          <div className="track-history-table">
            <table>
              <thead>
                <tr>
                  <th>Track ID</th>
                  <th>Frames Tracked</th>
                  <th>State</th>
                  <th>Position (X, Y)</th>
                  <th>Speed</th>
                </tr>
              </thead>
              <tbody>
                {results.tracks.map((track) => {
                  const stateNames = {
                    0: "NEW",
                    1: "TRACKED",
                    2: "LOST",
                  };
                  const stateClasses = {
                    0: "state-new",
                    1: "state-tracked",
                    2: "state-lost",
                  };
                  const stateName = stateNames[track.state] || "UNKNOWN";
                  const stateClass = stateClasses[track.state] || "";

                  return (
                    <tr key={track.id}>
                      <td className="track-id">#{track.id}</td>
                      <td>{track.frames_tracked || 0}</td>
                      <td>
                        <span className={`track-state ${stateClass}`}>
                          {stateName}
                        </span>
                      </td>
                      <td>
                        ({track.position[0].toFixed(0)},{" "}
                        {track.position[1].toFixed(0)})
                      </td>
                      <td>
                        {track.speed ? track.speed.toFixed(2) : "0.00"} px/s
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="tracking-legend">
            <span className="legend-item">
              <span
                className="color-box"
                style={{ backgroundColor: "#ff0000" }}
              ></span>
              <strong>NEW</strong> - Recently detected
            </span>
            <span className="legend-item">
              <span
                className="color-box"
                style={{ backgroundColor: "#00ff00" }}
              ></span>
              <strong>TRACKED</strong> - Actively tracked
            </span>
            <span className="legend-item">
              <span
                className="color-box"
                style={{ backgroundColor: "#ffff00" }}
              ></span>
              <strong>LOST</strong> - Temporarily lost
            </span>
          </p>
        </div>
      ) : (
        <div
          className="tracking-details"
          style={{
            background: "#f0f8ff",
            borderLeft: "4px solid #2196F3",
          }}
        >
          <h3>📊 Tracking Enabled</h3>
          <p style={{ margin: "10px 0", color: "#666" }}>
            ⏳ Waiting for objects to be detected and tracked...
          </p>
          <p
            style={{
              margin: "10px 0",
              fontSize: "0.9em",
              color: "#888",
            }}
          >
            Make sure:
            <br />
            • Camera is showing people/objects
            <br />
            • YOLO model is selected
            <br />
            • Tracking is enabled in settings
            <br />• Backend is processing frames (check debug info above)
          </p>
        </div>
      )}
    </>
  );
}

export default TrackingDetails;
