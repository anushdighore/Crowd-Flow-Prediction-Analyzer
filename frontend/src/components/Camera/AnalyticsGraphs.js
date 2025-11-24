import React from "react";
import SimpleChart from "../SimpleChart";
import AdvancedMetrics from "../AdvancedMetrics";

/**
 * AnalyticsGraphs Component
 * Displays real-time analytics: count trends, FPS trends, and advanced metrics
 */
function AnalyticsGraphs({
  countHistory,
  fpsHistory,
  enableTracking,
  results,
}) {
  return (
    <>
      {/* Advanced Crowd Analysis Metrics */}
      {enableTracking && results?.advanced_metrics && (
        <AdvancedMetrics
          densityMetrics={results.advanced_metrics.density_metrics}
          speedMetrics={results.advanced_metrics.speed_metrics}
        />
      )}

      {/* Real-time Analytics Graphs */}
      {countHistory.length > 1 && (
        <div className="graphs-section">
          <h3 className="graphs-title">📊 Real-Time Analytics</h3>
          <div className="graphs-container">
            <div className="graph-card">
              <SimpleChart
                data={countHistory}
                title="Crowd Count Over Time"
                color="#4CAF50"
                yLabel="People Count"
              />
            </div>
            <div className="graph-card">
              <SimpleChart
                data={fpsHistory}
                title="Processing Speed (FPS)"
                color="#2196F3"
                yLabel="Frames/Second"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AnalyticsGraphs;
