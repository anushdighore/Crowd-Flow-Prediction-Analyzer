import React from "react";
import AdvancedMetrics from "../AdvancedMetrics";
import "./VisualizationCards.css";

/**
 * MetricsCard - Reusable metrics display card
 * Works for: All detection modes
 * Shows: Timing, Density Stats, Tracking Data, Speed Metrics
 *
 * Props:
 * - isStreaming: boolean
 * - enableTracking: boolean
 * - results: detection results object
 */
function MetricsCard({ isStreaming, enableTracking, results }) {
  return (
    <div className="viz-card metrics-card">
      <div className="card-header">
        <h3>📈 Advanced Metrics</h3>
      </div>
      <div className="card-content">
        {isStreaming && enableTracking && results?.advanced_metrics ? (
          <AdvancedMetrics
            densityMetrics={results.advanced_metrics.density_metrics}
            speedMetrics={results.advanced_metrics.speed_metrics}
          />
        ) : isStreaming && results ? (
          <div className="basic-metrics">
            {/* Timing Metrics */}
            {results.timing && (
              <>
                <div className="metric-row">
                  <span>Inference Time:</span>
                  <span>{results.timing.inference_ms.toFixed(1)} ms</span>
                </div>
                <div className="metric-row">
                  <span>Total Time:</span>
                  <span>{results.timing.total_ms.toFixed(1)} ms</span>
                </div>
              </>
            )}

            {/* Density Map Stats */}
            {results.density_map_stats && (
              <>
                <div className="metric-section-title">Density Statistics</div>
                <div className="metric-row">
                  <span>Maximum:</span>
                  <span>{results.density_map_stats.max.toFixed(4)}</span>
                </div>
                <div className="metric-row">
                  <span>Mean:</span>
                  <span>{results.density_map_stats.mean.toFixed(4)}</span>
                </div>
                <div className="metric-row">
                  <span>Sum:</span>
                  <span>{results.density_map_stats.sum.toFixed(2)}</span>
                </div>
              </>
            )}

            {/* Confidence Stats */}
            {results.confidence_stats && (
              <>
                <div className="metric-section-title">
                  Confidence Statistics
                </div>
                <div className="metric-row">
                  <span>Average:</span>
                  <span>
                    {(results.confidence_stats.avg * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric-row">
                  <span>Minimum:</span>
                  <span>
                    {(results.confidence_stats.min * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric-row">
                  <span>Maximum:</span>
                  <span>
                    {(results.confidence_stats.max * 100).toFixed(1)}%
                  </span>
                </div>
              </>
            )}

            {/* Active Tracks Table */}
            {results.tracks && results.tracks.length > 0 && (
              <div className="tracks-table">
                <h4>Active Tracks</h4>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>State</th>
                      <th>Speed</th>
                      <th>Frames</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.tracks.slice(0, 5).map((track) => (
                      <tr key={track.id}>
                        <td>#{track.id}</td>
                        <td>
                          {track.state === 1
                            ? "✅ Tracked"
                            : track.state === 0
                            ? "🆕 New"
                            : "❌ Lost"}
                        </td>
                        <td>
                          {track.speed ? track.speed.toFixed(1) : "0"} px/s
                        </td>
                        <td>{track.frames_tracked || 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {results.tracks.length > 5 && (
                  <p className="table-note">
                    Showing 5 of {results.tracks.length} tracks
                  </p>
                )}
              </div>
            )}

            {/* Speed Statistics */}
            {results.speed_stats && (
              <>
                <div className="metric-section-title">Speed Analytics</div>
                <div className="metric-row">
                  <span>Average Speed:</span>
                  <span>{results.speed_stats.average.toFixed(2)} px/s</span>
                </div>
                <div className="metric-row">
                  <span>Maximum Speed:</span>
                  <span>{results.speed_stats.max.toFixed(2)} px/s</span>
                </div>
                <div className="metric-row">
                  <span>Minimum Speed:</span>
                  <span>{results.speed_stats.min.toFixed(2)} px/s</span>
                </div>
                <div className="metric-row">
                  <span>Std Deviation:</span>
                  <span>{results.speed_stats.std.toFixed(2)} px/s</span>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="card-placeholder">
            <div className="placeholder-icon">📈</div>
            <p>Start detection to see metrics</p>
            {!enableTracking && (
              <p className="hint-text">Enable tracking for advanced metrics</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MetricsCard;
