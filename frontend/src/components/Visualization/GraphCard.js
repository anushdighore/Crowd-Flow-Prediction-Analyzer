import React from "react";
import SimpleChart from "../SimpleChart";
import "./VisualizationCards.css";

/**
 * GraphCard - Reusable count over time graph card
 * Works for: All streaming modes (Webcam, External Camera, Video)
 *
 * Props:
 * - isStreaming: boolean
 * - countHistory: array of {time, count} objects
 * - title: string (optional custom title)
 */
function GraphCard({ isStreaming, countHistory, title = "Count Over Time" }) {
  return (
    <div className="viz-card graph-card">
      <div className="card-header">
        <h3>📊 {title}</h3>
      </div>
      <div className="card-content">
        {isStreaming && countHistory && countHistory.length > 0 ? (
          <div className="graph-container">
            <SimpleChart data={countHistory} />
            <div className="graph-stats">
              <div className="graph-stat">
                <span>Data Points:</span>
                <span>{countHistory.length}</span>
              </div>
              <div className="graph-stat">
                <span>Current:</span>
                <span>{countHistory[countHistory.length - 1]?.count || 0}</span>
              </div>
              <div className="graph-stat">
                <span>Average:</span>
                <span>
                  {(
                    countHistory.reduce((sum, item) => sum + item.count, 0) /
                    countHistory.length
                  ).toFixed(1)}
                </span>
              </div>
              <div className="graph-stat">
                <span>Peak:</span>
                <span>
                  {Math.max(...countHistory.map((item) => item.count))}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="card-placeholder">
            <div className="placeholder-icon">📊</div>
            <p>Start streaming to see real-time graph</p>
            <p className="hint-text">Shows last 30 data points</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default GraphCard;
