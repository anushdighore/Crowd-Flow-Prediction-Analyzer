import { Map } from "lucide-react";

export default function HeatmapPanel() {
  return (
    <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b border-border">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <Map className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">College Density Heatmap</h3>
        </div>

        {/* Heatmap Area */}
        <div className="p-6 flex-1 flex items-center justify-center bg-gradient-to-b from-background to-input/30 relative min-h-96">
          {/* Heatmap visualization placeholder */}
          <svg
            className="w-full h-full max-w-sm"
            viewBox="0 0 400 300"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* College area outline */}
            <rect
              x="40"
              y="40"
              width="320"
              height="220"
              fill="none"
              stroke="rgb(34, 211, 238)"
              strokeWidth="2"
              opacity="0.3"
            />

            {/* Building representations with gradient fills */}
            <rect
              x="60"
              y="60"
              width="80"
              height="60"
              fill="url(#heatGrad1)"
              opacity="0.6"
            />
            <rect
              x="170"
              y="60"
              width="100"
              height="80"
              fill="url(#heatGrad2)"
              opacity="0.8"
            />
            <rect
              x="290"
              y="80"
              width="50"
              height="60"
              fill="url(#heatGrad1)"
              opacity="0.5"
            />
            <rect
              x="60"
              y="150"
              width="120"
              height="100"
              fill="url(#heatGrad3)"
              opacity="0.7"
            />
            <rect
              x="210"
              y="160"
              width="130"
              height="80"
              fill="url(#heatGrad2)"
              opacity="0.6"
            />

            {/* Gradient definitions */}
            <defs>
              <linearGradient id="heatGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgb(34, 211, 238)" stopOpacity="0.3" />
                <stop offset="100%" stopColor="rgb(34, 211, 238)" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="heatGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgb(59, 130, 246)" stopOpacity="0.4" />
                <stop offset="100%" stopColor="rgb(34, 211, 238)" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="heatGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgb(34, 211, 238)" stopOpacity="0.5" />
                <stop offset="100%" stopColor="rgb(59, 130, 246)" stopOpacity="0.8" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Legend */}
        <div className="p-6 border-t border-border bg-gradient-to-b from-transparent to-neon-cyan/5">
          <p className="text-xs font-semibold text-muted-foreground mb-3">
            DENSITY LEGEND
          </p>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-gradient-to-r from-neon-cyan to-neon-blue opacity-40" />
              <span className="text-xs text-muted-foreground">Low Density</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-gradient-to-r from-neon-cyan to-neon-blue opacity-70" />
              <span className="text-xs text-muted-foreground">Medium Density</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100" />
              <span className="text-xs text-muted-foreground">High Density</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
