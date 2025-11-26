import Header from "@/components/ui/Header";
import KPICard from "@/components/dashboard/KPICard";
import CameraConnectCard from "@/components/dashboard/CameraConnectCard";
import MediaUploadCard from "@/components/dashboard/MediaUploadCard";
import ModelSelector from "@/components/dashboard/ModelSelector";
import TestRoomPanel from "@/components/dashboard/TestRoomPanel";
import LiveFlowPanel from "@/components/dashboard/LiveFlowPanel";
import HeatmapPanel from "@/components/dashboard/HeatmapPanel";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import SystemPerformancePanel from "@/components/dashboard/SystemPerformancePanel";
import ChartsPanel from "@/components/dashboard/ChartsPanel";
import ReportsPanel from "@/components/dashboard/ReportsPanel";
import {
  Users,
  Zap,
  Camera,
  Activity,
} from "lucide-react";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-background dark">
      <Header />

      {/* Main Dashboard */}
      <main className="pt-20 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Dashboard Header */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">
                  Dashboard
                </h1>
                <p className="text-muted-foreground">
                  Real-time crowd monitoring & analytics
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground mb-1">System Time</p>
                <p className="text-2xl font-bold text-neon-cyan">
                  {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>

          {/* KPI Metrics Row */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Key Performance Indicators
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard
                icon={Users}
                label="Real-Time People Count"
                value={1247}
                unit="people"
                trend="up"
                description="Currently detected"
              />
              <KPICard
                icon={Zap}
                label="FPS & Processing Delay"
                value={45}
                unit="FPS"
                trend="stable"
                description="8.2ms latency"
              />
              <KPICard
                icon={Camera}
                label="Active Camera Status"
                value={0}
                unit="cameras"
                trend="down"
                description="Ready to connect"
              />
              <KPICard
                icon={Activity}
                label="Heatmap Refresh Status"
                value={"Live"}
                trend="stable"
                description="Updating in real-time"
              />
            </div>
          </section>

          {/* Camera & Upload Section */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Input Configuration
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <CameraConnectCard />
              <MediaUploadCard />
            </div>
          </section>

          {/* Model & Test Room Section */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Model Configuration & Testing
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <ModelSelector />
              <TestRoomPanel />
            </div>
          </section>

          {/* Live Monitoring Section */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Live Monitoring
            </h2>
            <div className="grid lg:grid-cols-2 gap-6">
              <LiveFlowPanel />
              <HeatmapPanel />
            </div>
          </section>

          {/* Alerts & Performance Section */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Alerts & Performance
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <AlertsPanel />
              <SystemPerformancePanel />
            </div>
          </section>

          {/* Analytics & Charts Section */}
          <section className="mb-12">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Analytics & Visualizations
            </h2>
            <ChartsPanel />
          </section>

          {/* Reports Section */}
          <section>
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <div className="w-1 h-6 bg-gradient-to-b from-neon-cyan to-neon-blue rounded-full" />
              Reports & Export
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <ReportsPanel />
              <div className="relative rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden p-6">
                <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10">
                  <h3 className="font-bold text-foreground mb-4">Quick Stats</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                      <span className="text-sm text-muted-foreground">
                        Total Detections Today
                      </span>
                      <span className="font-bold text-neon-cyan">28,450</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                      <span className="text-sm text-muted-foreground">
                        Peak Density
                      </span>
                      <span className="font-bold text-neon-blue">2,847</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                      <span className="text-sm text-muted-foreground">
                        Avg Response Time
                      </span>
                      <span className="font-bold text-neon-cyan">8.2ms</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                      <span className="text-sm text-muted-foreground">
                        Uptime
                      </span>
                      <span className="font-bold text-green-400">99.8%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
