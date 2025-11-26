import { FileDown, Download } from "lucide-react";

export default function ReportsPanel() {
  return (
    <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300 p-6">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <FileDown className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">Reports Module</h3>
        </div>

        {/* Description */}
        <p className="text-sm text-muted-foreground mb-6">
          Export comprehensive analytics and monitoring data in your preferred
          format.
        </p>

        {/* Export Options */}
        <div className="space-y-3">
          <button className="w-full relative px-4 py-3 font-medium text-background rounded-lg overflow-hidden group/btn hover:shadow-neon-cyan transition-all flex items-center justify-center gap-2">
            <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover/btn:opacity-90 transition-opacity" />
            <span className="relative flex items-center gap-2">
              <Download className="w-5 h-5" />
              Export as PDF
            </span>
          </button>

          <button className="w-full px-4 py-3 font-medium text-foreground border border-neon-blue/50 rounded-lg hover:bg-neon-blue/10 transition-colors flex items-center justify-center gap-2">
            <Download className="w-5 h-5" />
            Export as CSV
          </button>
        </div>

        {/* Additional Info */}
        <div className="mt-6 p-4 rounded-lg bg-background border border-border">
          <p className="text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Last Export:</span>{" "}
            Today at 2:15 PM
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            Includes real-time counts, flow analytics, heatmaps, and system
            performance metrics.
          </p>
        </div>
      </div>
    </div>
  );
}
