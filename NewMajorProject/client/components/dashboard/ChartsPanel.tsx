import { TrendingUp } from "lucide-react";

export default function ChartsPanel() {
  return (
    <div className="space-y-6">
      {/* People Count Over Time */}
      <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300 p-6">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-foreground">
              People Count Over Time
            </h3>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-neon-cyan" />
              <span className="text-xs font-semibold text-neon-cyan">
                +8.2%
              </span>
            </div>
          </div>

          {/* Chart Placeholder */}
          <svg
            className="w-full h-64"
            viewBox="0 0 400 200"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Grid lines */}
            {[...Array(5)].map((_, i) => (
              <line
                key={`h-${i}`}
                x1="0"
                y1={40 * (i + 1)}
                x2="400"
                y2={40 * (i + 1)}
                stroke="rgba(34, 211, 238, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Chart line */}
            <polyline
              points="20,120 60,100 100,80 140,90 180,70 220,60 260,75 300,50 340,65 380,40"
              fill="none"
              stroke="url(#lineGrad)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Gradient fill under line */}
            <polygon
              points="20,120 60,100 100,80 140,90 180,70 220,60 260,75 300,50 340,65 380,40 380,200 20,200"
              fill="url(#areaGrad)"
              opacity="0.3"
            />

            {/* Gradient definitions */}
            <defs>
              <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(34, 211, 238)" />
                <stop offset="100%" stopColor="rgb(59, 130, 246)" />
              </linearGradient>
              <linearGradient id="areaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(34, 211, 238)" stopOpacity="0.6" />
                <stop offset="100%" stopColor="rgb(59, 130, 246)" stopOpacity="0.2" />
              </linearGradient>
            </defs>
          </svg>

          {/* X-axis labels */}
          <div className="flex justify-between text-xs text-muted-foreground mt-2 px-2">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>24:00</span>
          </div>
        </div>
      </div>

      {/* Flow Speed Over Time */}
      <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300 p-6">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-foreground">Flow Speed Over Time</h3>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-neon-blue" />
              <span className="text-xs font-semibold text-neon-blue">+3.1%</span>
            </div>
          </div>

          {/* Chart Placeholder */}
          <svg
            className="w-full h-64"
            viewBox="0 0 400 200"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Grid lines */}
            {[...Array(5)].map((_, i) => (
              <line
                key={`h2-${i}`}
                x1="0"
                y1={40 * (i + 1)}
                x2="400"
                y2={40 * (i + 1)}
                stroke="rgba(34, 211, 238, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Chart line */}
            <polyline
              points="20,140 60,120 100,110 140,130 180,100 220,90 260,110 300,80 340,95 380,70"
              fill="none"
              stroke="url(#lineGrad2)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Gradient fill under line */}
            <polygon
              points="20,140 60,120 100,110 140,130 180,100 220,90 260,110 300,80 340,95 380,70 380,200 20,200"
              fill="url(#areaGrad2)"
              opacity="0.3"
            />

            {/* Gradient definitions */}
            <defs>
              <linearGradient id="lineGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(59, 130, 246)" />
                <stop offset="100%" stopColor="rgb(34, 211, 238)" />
              </linearGradient>
              <linearGradient id="areaGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(59, 130, 246)" stopOpacity="0.6" />
                <stop offset="100%" stopColor="rgb(34, 211, 238)" stopOpacity="0.2" />
              </linearGradient>
            </defs>
          </svg>

          {/* X-axis labels */}
          <div className="flex justify-between text-xs text-muted-foreground mt-2 px-2">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>24:00</span>
          </div>
        </div>
      </div>

      {/* Density Variation */}
      <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300 p-6">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

        {/* Content */}
        <div className="relative z-10">
          <h3 className="font-bold text-foreground mb-6">Density Variation</h3>

          {/* Bar Chart */}
          <div className="space-y-3">
            {[
              { label: "Main Hall", value: 75 },
              { label: "Library", value: 45 },
              { label: "Cafeteria", value: 60 },
              { label: "Lobby", value: 80 },
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-muted-foreground">
                    {item.label}
                  </span>
                  <span className="text-sm font-bold text-foreground">
                    {item.value}%
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-input overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-neon-cyan to-neon-blue transition-all duration-500"
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
