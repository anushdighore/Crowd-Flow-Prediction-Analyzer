import { useState } from "react";
import { AlertCircle, Clock, X } from "lucide-react";

interface Alert {
  id: string;
  timestamp: string;
  message: string;
}

export default function AlertsPanel() {
  const [threshold, setThreshold] = useState(50);
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: "1",
      timestamp: "2:34 PM",
      message: "Capacity threshold exceeded in Building A",
    },
    {
      id: "2",
      timestamp: "1:15 PM",
      message: "High crowd density detected near main entrance",
    },
  ]);

  const handleRemoveAlert = (id: string) => {
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  return (
    <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b border-border">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <AlertCircle className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">Count Threshold Alert</h3>
        </div>

        {/* Threshold Settings */}
        <div className="p-6 border-b border-border">
          <label className="block text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wider">
            Alert Threshold
          </label>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="500"
                value={threshold}
                onChange={(e) => setThreshold(parseInt(e.target.value))}
                className="flex-1 h-2 bg-input rounded-lg appearance-none cursor-pointer accent-neon-cyan"
              />
              <div className="flex items-center justify-center w-16 h-10 rounded-lg bg-input border border-border">
                <span className="font-bold text-foreground text-lg">
                  {threshold}
                </span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Alert when people count exceeds {threshold}
            </p>
          </div>
        </div>

        {/* Alert Log */}
        <div className="p-6 flex-1 overflow-y-auto">
          <p className="text-xs font-semibold text-muted-foreground mb-4 uppercase tracking-wider">
            Alert Log
          </p>

          {alerts.length > 0 ? (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start justify-between gap-2"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Clock className="w-3 h-3 text-red-400 flex-shrink-0" />
                      <span className="text-xs font-semibold text-red-400">
                        {alert.timestamp}
                      </span>
                    </div>
                    <p className="text-xs text-foreground">{alert.message}</p>
                  </div>
                  <button
                    onClick={() => handleRemoveAlert(alert.id)}
                    className="p-1 hover:bg-red-500/20 rounded transition-colors flex-shrink-0"
                  >
                    <X className="w-3 h-3 text-muted-foreground" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-24">
              <p className="text-sm text-muted-foreground text-center">
                No alerts. All systems normal.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
