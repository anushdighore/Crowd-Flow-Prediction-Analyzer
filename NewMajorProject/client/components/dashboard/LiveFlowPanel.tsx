import { Video, Circle } from "lucide-react";

export default function LiveFlowPanel() {
  return (
    <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-neon-cyan/10">
              <Video className="w-6 h-6 text-neon-cyan" />
            </div>
            <div>
              <h3 className="font-bold text-foreground">
                Real-Time Crowd Flow & Detection
              </h3>
              <p className="text-xs text-muted-foreground">Single Camera</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-red-400">LIVE</span>
          </div>
        </div>

        {/* Video Feed Area */}
        <div className="p-6 flex-1 flex items-center justify-center bg-gradient-to-b from-background to-input/30 relative min-h-96">
          {/* Animated grid background */}
          <svg
            className="absolute inset-0 w-full h-full opacity-5"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="grid2"
                width="40"
                height="40"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 40 0 L 0 0 0 40"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid2)" />
          </svg>

          {/* Placeholder content */}
          <div className="relative text-center">
            <div className="mb-4 inline-block p-4 rounded-lg bg-neon-cyan/10">
              <Video className="w-8 h-8 text-neon-cyan" />
            </div>
            <p className="text-sm text-muted-foreground">
              Connect a camera to start monitoring
            </p>
          </div>
        </div>

        {/* Stats Footer */}
        <div className="p-6 border-t border-border bg-gradient-to-b from-transparent to-neon-cyan/5 grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Count</p>
            <p className="text-2xl font-bold text-neon-cyan">0</p>
          </div>
          <div className="text-center border-l border-r border-border">
            <p className="text-xs text-muted-foreground mb-1">FPS</p>
            <p className="text-2xl font-bold text-neon-cyan">--</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Status</p>
            <div className="flex items-center justify-center gap-1">
              <Circle className="w-2 h-2 text-yellow-500 fill-yellow-500" />
              <span className="text-xs text-yellow-400 font-medium">Idle</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
