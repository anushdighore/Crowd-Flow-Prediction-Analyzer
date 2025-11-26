import React, { useState, useEffect } from "react";

const OccupancyWidget = ({
  occupancyData,
  alertData,
  densityHeatmap,
  occupancyStatistics,
  occupancyAlerts,
  historicalDataAvailable,
  occupancyTimestamp,
}) => {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [alertHistory, setAlertHistory] = useState([]);

  // Update alert history when new alerts arrive
  useEffect(() => {
    if (occupancyAlerts && occupancyAlerts.length > 0) {
      setAlertHistory((prev) => [...prev.slice(-9), ...occupancyAlerts]); // Keep last 10 alerts
    }
  }, [occupancyAlerts]);

  if (!occupancyData) {
    return (
      <div
        style={{
          backgroundColor: "#f8f9fa",
          border: "2px solid #dee2e6",
          borderRadius: "12px",
          padding: "1.5rem",
          margin: "1rem 0",
          textAlign: "center",
          color: "#6c757d",
        }}
      >
        <div style={{ fontSize: "1.1rem" }}>📊 Enhanced Occupancy Monitor</div>
        <div style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
          Start streaming to see occupancy data with density visualization
        </div>
      </div>
    );
  }

  const {
    current_count,
    average_count,
    occupancy_percentage,
    alert_state,
    alert_triggered,
    max_capacity,
    percentage,
    count,
  } = occupancyData;

  // Use new data structure if available, fallback to old
  const currentCount = count || current_count || 0;
  const currentPercentage = percentage || occupancy_percentage || 0;
  const maxCapacity = max_capacity || 100;

  // Determine status color
  let statusColor = "#28a745"; // Green (normal)
  let statusIcon = "✅";
  let statusText = "Normal";

  if (alert_state || alert_triggered) {
    statusColor = "#dc3545"; // Red (alert)
    statusIcon = "🚨";
    statusText = "High Occupancy";
  } else if (currentPercentage >= 80) {
    statusColor = "#ffc107"; // Yellow (warning)
    statusIcon = "⚠️";
    statusText = "Warning";
  }

  // Progress bar color
  let progressColor = "#28a745";
  if (currentPercentage >= 80) {
    progressColor = "#dc3545";
  } else if (currentPercentage >= 70) {
    progressColor = "#ffc107";
  }

  return (
    <div
      style={{
        backgroundColor: "#ffffff",
        border: `2px solid ${statusColor}`,
        borderRadius: "12px",
        padding: "1.5rem",
        margin: "1rem 0",
        boxShadow: alert_triggered
          ? "0 4px 12px rgba(220, 53, 69, 0.3)"
          : "0 2px 8px rgba(0,0,0,0.1)",
        transition: "all 0.3s ease",
      }}
    >
      {/* Header with Toggle Buttons */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <div
          style={{
            fontSize: "1.3rem",
            fontWeight: "bold",
            color: "#333",
          }}
        >
          📊 Enhanced Occupancy Monitor
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          {/* Toggle Buttons */}
          {densityHeatmap && (
            <button
              onClick={() => setShowHeatmap(!showHeatmap)}
              style={{
                padding: "0.25rem 0.5rem",
                backgroundColor: showHeatmap ? "#007bff" : "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
                fontSize: "0.8rem",
                cursor: "pointer",
              }}
            >
              📊 Heatmap
            </button>
          )}
          {occupancyStatistics && (
            <button
              onClick={() => setShowStats(!showStats)}
              style={{
                padding: "0.25rem 0.5rem",
                backgroundColor: showStats ? "#007bff" : "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
                fontSize: "0.8rem",
                cursor: "pointer",
              }}
            >
              📈 Stats
            </button>
          )}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.25rem 0.75rem",
              backgroundColor: statusColor,
              color: "white",
              borderRadius: "20px",
              fontSize: "0.9rem",
              fontWeight: "bold",
            }}
          >
            {statusIcon} {statusText}
          </div>
        </div>
      </div>

      {/* Alert Notifications */}
      {occupancyAlerts && occupancyAlerts.length > 0 && (
        <div
          style={{
            backgroundColor:
              occupancyAlerts[0].level === "critical" ? "#f8d7da" : "#fff3cd",
            border: `1px solid ${
              occupancyAlerts[0].level === "critical" ? "#f5c6cb" : "#ffeaa7"
            }`,
            borderRadius: "8px",
            padding: "0.75rem",
            marginBottom: "1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.2rem" }}>
              {occupancyAlerts[0].level === "critical" ? "🚨" : "⚠️"}
            </span>
            <div>
              <div style={{ fontWeight: "bold", fontSize: "0.9rem" }}>
                {occupancyAlerts[0].level === "critical"
                  ? "Critical Alert"
                  : "Warning"}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#666" }}>
                {occupancyAlerts[0].message}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Occupancy Display */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#333" }}>
            {currentCount}
          </div>
          <div style={{ fontSize: "0.9rem", color: "#666" }}>
            of {maxCapacity} people
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div
            style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              color: statusColor,
            }}
          >
            {currentPercentage.toFixed(1)}%
          </div>
          <div style={{ fontSize: "0.8rem", color: "#666" }}>Occupancy</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          backgroundColor: "#e9ecef",
          borderRadius: "10px",
          height: "12px",
          overflow: "hidden",
          marginBottom: "1rem",
        }}
      >
        <div
          style={{
            backgroundColor: progressColor,
            height: "100%",
            width: `${Math.min(currentPercentage, 100)}%`,
            transition: "width 0.3s ease",
            borderRadius: "10px",
          }}
        />
      </div>

      {/* Timestamp */}
      {occupancyTimestamp && (
        <div
          style={{
            fontSize: "0.75rem",
            color: "#999",
            textAlign: "center",
            marginBottom: "0.5rem",
          }}
        >
          Last updated: {new Date(occupancyTimestamp).toLocaleTimeString()}
        </div>
      )}

      {/* Density Heatmap */}
      {showHeatmap && densityHeatmap && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              marginBottom: "0.5rem",
              color: "#333",
            }}
          >
            📊 Density Heatmap
          </div>
          <img
            src={densityHeatmap}
            alt="Density Heatmap"
            style={{
              width: "100%",
              borderRadius: "4px",
              border: "1px solid #ddd",
            }}
          />
          <div
            style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}
          >
            Real-time density visualization (Red = High density, Blue = Low
            density)
          </div>
        </div>
      )}

      {/* Statistics Panel */}
      {showStats && occupancyStatistics && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              marginBottom: "0.5rem",
              color: "#333",
            }}
          >
            📈 Occupancy Statistics
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "0.5rem",
            }}
          >
            <div>
              <div style={{ fontSize: "0.8rem", color: "#666" }}>
                Peak Count
              </div>
              <div
                style={{
                  fontSize: "1.1rem",
                  fontWeight: "bold",
                  color: "#333",
                }}
              >
                {occupancyStatistics.peak_count || 0}
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#666" }}>Peak %</div>
              <div
                style={{
                  fontSize: "1.1rem",
                  fontWeight: "bold",
                  color: "#333",
                }}
              >
                {(occupancyStatistics.peak_percentage || 0).toFixed(1)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#666" }}>
                Average Count
              </div>
              <div
                style={{
                  fontSize: "1.1rem",
                  fontWeight: "bold",
                  color: "#333",
                }}
              >
                {(occupancyStatistics.average_count || 0).toFixed(1)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.8rem", color: "#666" }}>Average %</div>
              <div
                style={{
                  fontSize: "1.1rem",
                  fontWeight: "bold",
                  color: "#333",
                }}
              >
                {(occupancyStatistics.average_percentage || 0).toFixed(1)}%
              </div>
            </div>
          </div>
          {historicalDataAvailable && (
            <div
              style={{
                marginTop: "0.5rem",
                fontSize: "0.8rem",
                color: "#28a745",
                fontWeight: "bold",
              }}
            >
              ✓ Historical data tracking active
            </div>
          )}
        </div>
      )}

      {/* Alert History */}
      {alertHistory.length > 0 && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              marginBottom: "0.5rem",
              color: "#333",
            }}
          >
            🚨 Recent Alerts
          </div>
          <div style={{ maxHeight: "150px", overflowY: "auto" }}>
            {alertHistory
              .slice(-5)
              .reverse()
              .map((alert, index) => (
                <div
                  key={index}
                  style={{
                    padding: "0.5rem",
                    backgroundColor:
                      alert.level === "critical" ? "#f8d7da" : "#fff3cd",
                    border: `1px solid ${
                      alert.level === "critical" ? "#f5c6cb" : "#ffeaa7"
                    }`,
                    borderRadius: "4px",
                    marginBottom: "0.25rem",
                    fontSize: "0.8rem",
                  }}
                >
                  <div style={{ fontWeight: "bold" }}>
                    {alert.level === "critical" ? "🚨 Critical" : "⚠️ Warning"}
                  </div>
                  <div>{alert.message}</div>
                  <div style={{ fontSize: "0.7rem", color: "#666" }}>
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OccupancyWidget;
