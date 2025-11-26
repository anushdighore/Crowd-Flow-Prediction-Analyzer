import React, { useMemo } from "react";

const CARD_STYLE = {
  background: "white",
  borderRadius: "12px",
  padding: "1.5rem",
  boxShadow: "0 12px 32px rgba(15,23,42,0.08)",
};

const Sparkline = ({ series = [], color = "#2563eb" }) => {
  const width = 240;
  const height = 80;

  if (!series.length) {
    return (
      <div
        style={{ color: "#94a3b8", fontSize: "0.85rem", marginTop: "0.5rem" }}
      >
        Waiting for live data...
      </div>
    );
  }

  const min = Math.min(...series);
  const max = Math.max(...series);
  const range = max - min || 1;

  const points = series
    .map((value, index) => {
      const x = (index / (series.length - 1 || 1)) * width;
      const normalized = (value - min) / range;
      const y = height - normalized * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} role="img" aria-label="Sparkline trend">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

const MetricCard = ({ title, unit, series, color, latest }) => (
  <div style={CARD_STYLE}>
    <p
      style={{
        textTransform: "uppercase",
        letterSpacing: "0.08em",
        fontSize: "0.75rem",
        color: "#94a3b8",
        margin: 0,
      }}
    >
      {title}
    </p>
    <div style={{ display: "flex", alignItems: "baseline", gap: "0.3rem" }}>
      <span style={{ fontSize: "2rem", fontWeight: 700 }}>
        {latest ?? "--"}
      </span>
      <span style={{ color: "#94a3b8" }}>{unit}</span>
    </div>
    <Sparkline series={series} color={color} />
  </div>
);

const WebcamMetricsChart = ({ history = [] }) => {
  const countSeries = useMemo(
    () => history.map((point) => point.count ?? 0),
    [history]
  );
  const latencySeries = useMemo(
    () => history.map((point) => point.inference ?? 0),
    [history]
  );
  const fpsSeries = useMemo(
    () => history.map((point) => point.fps ?? 0),
    [history]
  );

  const latest = history[history.length - 1] || {};

  return (
    <section
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: "1.5rem",
        marginBottom: "2rem",
      }}
    >
      <MetricCard
        title="Crowd Count"
        unit="people"
        series={countSeries}
        color="#6366f1"
        latest={latest.count}
      />
      <MetricCard
        title="Latency"
        unit="ms"
        series={latencySeries}
        color="#f97316"
        latest={latest.inference}
      />
      <MetricCard
        title="FPS"
        unit="frames"
        series={fpsSeries}
        color="#10b981"
        latest={latest.fps}
      />
    </section>
  );
};

export default WebcamMetricsChart;
