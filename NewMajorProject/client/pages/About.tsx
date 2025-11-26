import Header from "@/components/ui/Header";
import {
  Eye,
  Zap,
  Activity,
  Camera,
  Upload,
  Settings,
  TrendingUp,
  AlertCircle,
} from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "Live People Count (Real-Time)",
    description:
      "Instantaneous accurate detection and counting of people in monitored areas with high precision.",
  },
  {
    icon: Zap,
    title: "Movement Flow Visualization",
    description:
      "Visual representation of crowd movement patterns and flow directions across campus areas.",
  },
  {
    icon: Activity,
    title: "Heatmap Highlighting",
    description:
      "Density visualization showing high-traffic areas and crowd concentration zones.",
  },
  {
    icon: Camera,
    title: "Room-Level Exact Counting",
    description:
      "Precise per-room person count detection with frame-by-frame accuracy.",
  },
  {
    icon: Upload,
    title: "IP Camera & Video Upload Support",
    description:
      "Flexible input options supporting IP webcam streams and video file uploads.",
  },
  {
    icon: Settings,
    title: "DL Model Selection",
    description:
      "Choose from multiple detection models including YOLOv8, YOLOv10, and FasterRCNN.",
  },
];

export default function About() {
  return (
    <div className="min-h-screen bg-background dark">
      <Header />

      {/* Page Header */}
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 border-b border-border">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold mb-6">About This Project</h1>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-neon-cyan/30 bg-neon-cyan/5 mb-6">
            <span className="text-sm font-medium text-neon-cyan">
              Intelligent Campus Monitoring
            </span>
          </div>
        </div>
      </section>

      {/* Project Description */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="prose prose-invert max-w-none">
            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
              A real-time AI-powered platform for monitoring crowd density,
              people counting, and movement analytics within a college
              environment. This system leverages cutting-edge deep learning
              technology to provide institutional administrators with
              actionable insights into campus occupancy patterns, helping
              optimize space utilization, enhance safety, and improve
              operational efficiency.
            </p>
          </div>

          {/* Key Benefits */}
          <div className="grid md:grid-cols-2 gap-6 mt-12">
            {[
              {
                title: "Safety & Capacity",
                description:
                  "Monitor occupancy levels to prevent overcrowding and maintain safe conditions.",
              },
              {
                title: "Space Optimization",
                description:
                  "Understand usage patterns to better allocate and manage campus spaces.",
              },
              {
                title: "Real-Time Insights",
                description:
                  "Get immediate visibility into crowd movements and density changes.",
              },
              {
                title: "Data-Driven Decisions",
                description:
                  "Make informed decisions based on comprehensive analytics and reports.",
              },
            ].map((benefit, idx) => (
              <div
                key={idx}
                className="p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background"
              >
                <h3 className="font-bold text-foreground mb-2">
                  {benefit.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {benefit.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="mb-16">
            <h2 className="text-4xl font-bold mb-4">Comprehensive Features</h2>
            <p className="text-lg text-muted-foreground">
              A complete suite of tools for intelligent crowd monitoring
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="group p-8 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background hover:border-neon-cyan/50 hover:shadow-neon-cyan transition-all duration-300"
                >
                  <div className="mb-4 inline-block p-3 rounded-lg bg-neon-cyan/10 group-hover:bg-neon-cyan/20 transition-colors">
                    <Icon className="w-6 h-6 text-neon-cyan" />
                  </div>
                  <h3 className="font-bold text-lg text-foreground mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="mb-16">
            <h2 className="text-4xl font-bold mb-4">Technology Stack</h2>
            <p className="text-lg text-muted-foreground">
              Built with modern, enterprise-grade technologies
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { name: "Deep Learning", desc: "YOLOv8, YOLOv10, FasterRCNN" },
              { name: "Real-time Processing", desc: "GPU-accelerated inference" },
              {
                name: "Data Pipeline",
                desc: "Stream processing & analytics",
              },
              {
                name: "Analytics",
                desc: "Comprehensive dashboarding & reports",
              },
            ].map((tech, idx) => (
              <div
                key={idx}
                className="p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background text-center"
              >
                <h3 className="font-bold text-foreground mb-2">{tech.name}</h3>
                <p className="text-sm text-muted-foreground">{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* System Architecture Highlights */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-border">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-12">System Architecture</h2>

          <div className="space-y-6">
            {[
              {
                title: "Multi-Model Support",
                desc: "Flexible deep learning model selection for different detection scenarios and accuracy requirements.",
              },
              {
                title: "Real-Time Processing",
                desc:
                  "Low-latency video stream processing with immediate crowd analytics and alerts.",
              },
              {
                title: "Scalable Monitoring",
                desc:
                  "Support for multiple simultaneous camera feeds across different campus locations.",
              },
              {
                title: "Comprehensive Reporting",
                desc:
                  "Detailed analytics, historical data tracking, and exportable reports in multiple formats.",
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background"
              >
                <h3 className="font-bold text-foreground mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
