import { Camera } from "lucide-react";

export default function TestRoomPanel() {
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
              <Camera className="w-6 h-6 text-neon-cyan" />
            </div>
            <h3 className="font-bold text-foreground">Test Room – Exact Count</h3>
          </div>
        </div>

        {/* Image Preview Area */}
        <div className="p-6 flex-1 flex flex-col items-center justify-center bg-gradient-to-b from-background to-input/30">
          <svg
            className="w-16 h-16 text-muted-foreground/30 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p className="text-sm text-muted-foreground text-center">
            Upload an image from Media Upload section to analyze
          </p>
        </div>

        {/* Count Display */}
        <div className="px-6 py-8 border-t border-border bg-gradient-to-b from-transparent to-neon-cyan/5 text-center">
          <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wider">
            Detected Count
          </p>
          <div className="flex items-baseline justify-center gap-2">
            <span className="text-5xl font-bold text-neon-cyan">0</span>
            <span className="text-lg text-muted-foreground">people</span>
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            Accuracy: --% | Confidence: --%
          </p>
        </div>
      </div>
    </div>
  );
}
