import { Gauge, Zap } from "lucide-react";

export default function SystemPerformancePanel() {
  const metrics = [
    { label: "FPS", value: 45, max: 60, unit: "fps", color: "neon-cyan" },
    { label: "Latency", value: 8.2, max: 50, unit: "ms", color: "neon-blue" },
    { label: "CPU Usage", value: 65, max: 100, unit: "%", color: "neon-cyan" },
    { label: "GPU Usage", value: 78, max: 100, unit: "%", color: "neon-blue" },
  ];

  return (
    <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b border-border">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <Gauge className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">System Performance</h3>
        </div>

        {/* Metrics Grid */}
        <div className="p-6 space-y-4">
          {metrics.map((metric, idx) => (
            <div key={idx}>
              {/* Label and Value */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-muted-foreground">
                  {metric.label}
                </span>
                <span className="text-sm font-bold text-foreground">
                  {metric.value.toFixed(metric.label === "Latency" ? 1 : 0)}{" "}
                  <span className="text-xs text-muted-foreground">
                    {metric.unit}
                  </span>
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-input overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    metric.color === "neon-cyan"
                      ? "bg-gradient-to-r from-neon-cyan to-neon-blue"
                      : "bg-gradient-to-r from-neon-blue to-neon-cyan"
                  } transition-all duration-500`}
                  style={{
                    width: `${Math.min((metric.value / metric.max) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Status Footer */}
        <div className="p-6 border-t border-border bg-gradient-to-b from-transparent to-neon-cyan/5">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            <div>
              <p className="text-xs font-semibold text-foreground">
                System Status
              </p>
              <p className="text-xs text-muted-foreground">
                All systems operational
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
