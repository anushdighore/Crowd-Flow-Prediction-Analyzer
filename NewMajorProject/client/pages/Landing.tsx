import Header from "@/components/ui/Header";
import { Link } from "react-router-dom";
import { Activity, Radio } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-background dark">
      <Header />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-96 h-96 bg-neon-cyan/10 rounded-full blur-3xl" />
          <div className="absolute bottom-40 right-20 w-80 h-80 bg-neon-blue/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/3 w-72 h-72 bg-neon-cyan/5 rounded-full blur-3xl" />
        </div>

        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-16">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-neon-cyan/30 bg-neon-cyan/5 mb-6">
              <Radio className="w-4 h-4 text-neon-cyan" />
              <span className="text-sm font-medium text-neon-cyan">
                AI-Powered Monitoring
              </span>
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl sm:text-7xl font-bold mb-6 tracking-tight">
              <span className="text-foreground">Real-Time College</span>{" "}
              <span className="bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
                Crowd Monitoring
              </span>{" "}
              <span className="text-foreground">&amp; Flow Analytics</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-12">
              A real-time AI-powered platform for monitoring crowd density,
              people counting, and movement analytics within a college
              environment.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboard"
                className="relative px-8 py-3 font-semibold text-background rounded-lg overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover:opacity-90 transition-opacity" />
                <span className="relative flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Launch Dashboard
                </span>
              </Link>

              <button className="px-8 py-3 font-semibold text-foreground border border-neon-cyan/50 rounded-lg hover:bg-neon-cyan/10 transition-colors">
                Learn More
              </button>
            </div>
          </div>

          {/* Hero Graphic */}
          <div className="relative mt-20 rounded-2xl overflow-hidden border border-neon-cyan/20 bg-gradient-to-b from-card to-background backdrop-blur-xl">
            {/* Glass effect panel */}
            <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 via-transparent to-neon-blue/5" />

            {/* Dashboard Preview Mockup */}
            <div className="relative p-8 sm:p-12">
              <div className="aspect-video bg-gradient-to-br from-background to-card rounded-lg border border-neon-cyan/20 flex items-center justify-center">
                <div className="relative w-full h-full flex flex-col items-center justify-center">
                  {/* Animated grid background */}
                  <svg
                    className="absolute inset-0 w-full h-full opacity-10"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <defs>
                      <pattern
                        id="grid"
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
                    <rect width="100%" height="100%" fill="url(#grid)" />
                  </svg>

                  {/* Central AI visualization */}
                  <div className="relative">
                    <div className="absolute inset-0 bg-neon-cyan/20 rounded-full blur-3xl w-64 h-64" />
                    <div className="relative flex items-center justify-center w-64 h-64">
                      <div className="w-32 h-32 bg-gradient-to-br from-neon-cyan to-neon-blue rounded-lg opacity-50 blur-lg" />
                      <div className="absolute w-20 h-20 bg-neon-cyan rounded-lg" />
                    </div>
                  </div>

                  {/* Stats around */}
                  <div className="absolute top-8 left-8 text-center">
                    <div className="text-neon-cyan font-bold text-2xl">1,247</div>
                    <div className="text-xs text-muted-foreground">
                      People Detected
                    </div>
                  </div>
                  <div className="absolute bottom-8 right-8 text-center">
                    <div className="text-neon-blue font-bold text-2xl">45 FPS</div>
                    <div className="text-xs text-muted-foreground">Processing</div>
                  </div>
                  <div className="absolute top-8 right-8 text-center">
                    <div className="text-neon-cyan font-bold text-2xl">8.2ms</div>
                    <div className="text-xs text-muted-foreground">Latency</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Preview Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Everything you need for intelligent crowd management
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Activity,
                title: "Live People Count",
                description: "Real-time accurate people detection and counting",
              },
              {
                icon: Radio,
                title: "Movement Flow",
                description: "Visualize crowd movement patterns and flows",
              },
              {
                icon: Activity,
                title: "AI Models",
                description: "Multiple detection models (YOLOv8, YOLOv10, etc)",
              },
            ].map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="group p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background hover:border-neon-cyan/50 transition-all duration-300"
                >
                  <div className="mb-4 inline-block p-3 rounded-lg bg-neon-cyan/10 group-hover:bg-neon-cyan/20 transition-colors">
                    <Icon className="w-6 h-6 text-neon-cyan" />
                  </div>
                  <h3 className="font-bold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Monitor Your Campus?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Get started with our intelligent crowd monitoring system today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/dashboard"
              className="relative px-8 py-3 font-semibold text-background rounded-lg overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover:opacity-90 transition-opacity" />
              <span className="relative">Access Dashboard</span>
            </Link>
            <button className="px-8 py-3 font-semibold text-foreground border border-neon-cyan/50 rounded-lg hover:bg-neon-cyan/10 transition-colors">
              Contact Sales
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
