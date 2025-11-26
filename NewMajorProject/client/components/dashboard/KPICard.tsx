import { LucideIcon } from "lucide-react";

interface KPICardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "stable";
  description?: string;
}

export default function KPICard({
  icon: Icon,
  label,
  value,
  unit,
  trend,
  description,
}: KPICardProps) {
  return (
    <div className="relative p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10">
        {/* Header with icon */}
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-lg bg-neon-cyan/10 group-hover:bg-neon-cyan/20 transition-colors">
            <Icon className="w-6 h-6 text-neon-cyan" />
          </div>
          {trend && (
            <div className="text-xs font-semibold px-2 py-1 rounded-full">
              {trend === "up" && (
                <span className="text-green-400 bg-green-400/10">↑ +12%</span>
              )}
              {trend === "down" && (
                <span className="text-red-400 bg-red-400/10">↓ -8%</span>
              )}
              {trend === "stable" && (
                <span className="text-yellow-400 bg-yellow-400/10">→ Stable</span>
              )}
            </div>
          )}
        </div>

        {/* Label */}
        <p className="text-sm text-muted-foreground mb-2">{label}</p>

        {/* Value */}
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-3xl font-bold text-foreground">{value}</span>
          {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
        </div>

        {/* Description */}
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}
