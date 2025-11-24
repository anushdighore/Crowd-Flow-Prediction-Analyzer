import React from "react";
import "../styles/AdvancedMetrics.css";

/**
 * AdvancedMetrics - Display advanced crowd analysis metrics (density & speed)
 *
 * @param {Object} densityMetrics - Density metrics from PedPy
 * @param {Object} speedMetrics - Speed metrics from PedPy
 */
const AdvancedMetrics = ({ densityMetrics, speedMetrics }) => {
  if (!densityMetrics && !speedMetrics) {
    return null;
  }

  // Helper function to safely format numbers
  const formatNumber = (value, decimals = 4) => {
    if (value === null || value === undefined)
      return "0".padEnd(decimals + 2, "0");
    const num = typeof value === "number" ? value : parseFloat(value);
    return isNaN(num) ? "0".padEnd(decimals + 2, "0") : num.toFixed(decimals);
  };

  return (
    <div className="advanced-metrics-container">
      <h3 className="metrics-title">Advanced Crowd Analysis</h3>

      {/* Density Metrics Section */}
      {densityMetrics && (
        <div className="metrics-section">
          <h4 className="section-title">
            <span className="icon">📊</span> Density Metrics
          </h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Classic Density</div>
              <div className="metric-value">
                {formatNumber(densityMetrics.classic_density, 4)}
              </div>
              <div className="metric-unit">ped/m²</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Voronoi Density</div>
              <div className="metric-value">
                {formatNumber(densityMetrics.voronoi_density, 4)}
              </div>
              <div className="metric-unit">ped/m²</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Voronoi (Cutoff)</div>
              <div className="metric-value">
                {formatNumber(densityMetrics.voronoi_density_cutoff, 4)}
              </div>
              <div className="metric-unit">ped/m²</div>
            </div>
          </div>
        </div>
      )}

      {/* Speed Metrics Section */}
      {speedMetrics && (
        <div className="metrics-section">
          <h4 className="section-title">
            <span className="icon">🚶</span> Speed Metrics
          </h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Mean Speed</div>
              <div className="metric-value">
                {formatNumber(speedMetrics.mean_speed, 3)}
              </div>
              <div className="metric-unit">m/s</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Voronoi Speed</div>
              <div className="metric-value">
                {formatNumber(speedMetrics.voronoi_speed, 3)}
              </div>
              <div className="metric-unit">m/s</div>
            </div>

            {speedMetrics.mean_speed_direction !== undefined && (
              <div className="metric-card">
                <div className="metric-label">Mean Speed (Dir)</div>
                <div className="metric-value">
                  {formatNumber(speedMetrics.mean_speed_direction, 3)}
                </div>
                <div className="metric-unit">m/s</div>
              </div>
            )}

            {speedMetrics.voronoi_speed_direction !== undefined && (
              <div className="metric-card">
                <div className="metric-label">Voronoi Speed (Dir)</div>
                <div className="metric-value">
                  {formatNumber(speedMetrics.voronoi_speed_direction, 3)}
                </div>
                <div className="metric-unit">m/s</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Footer */}
      <div className="metrics-info">
        <small>
          💡 Metrics calculated using PedPy pedestrian dynamics library
        </small>
      </div>
    </div>
  );
};

export default AdvancedMetrics;
