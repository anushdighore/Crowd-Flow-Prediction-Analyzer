import { useState } from "react";
import { Settings, Check } from "lucide-react";

const models = [
  { id: "yolov8", name: "YOLOv8", description: "Balanced speed and accuracy" },
  { id: "yolov10", name: "YOLOv10", description: "Latest improvements" },
  { id: "fasterrcnn", name: "FasterRCNN", description: "High accuracy mode" },
  { id: "custom", name: "Custom Model", description: "Your own trained model" },
];

export default function ModelSelector() {
  const [selectedModel, setSelectedModel] = useState("yolov8");
  const [isOpen, setIsOpen] = useState(false);

  const activeModel = models.find((m) => m.id === selectedModel);

  return (
    <div className="relative p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <Settings className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">Detection Model</h3>
        </div>

        {/* Model Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground text-sm flex items-center justify-between hover:border-neon-cyan/50 transition-colors"
          >
            <div className="text-left">
              <p className="font-semibold">{activeModel?.name}</p>
              <p className="text-xs text-muted-foreground">
                {activeModel?.description}
              </p>
            </div>
            <svg
              className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>

          {/* Dropdown Menu */}
          {isOpen && (
            <div className="absolute top-full left-0 right-0 mt-2 rounded-lg bg-card border border-neon-cyan/20 shadow-lg z-50 overflow-hidden">
              {models.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setIsOpen(false);
                  }}
                  className="w-full px-4 py-3 text-left hover:bg-neon-cyan/10 transition-colors border-b border-border last:border-b-0 flex items-start justify-between"
                >
                  <div>
                    <p className="font-semibold text-foreground text-sm">
                      {model.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {model.description}
                    </p>
                  </div>
                  {selectedModel === model.id && (
                    <Check className="w-4 h-4 text-neon-cyan flex-shrink-0 mt-0.5" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Model Info */}
        <div className="mt-4 p-4 rounded-lg bg-background border border-border">
          <p className="text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Selected:</span> {activeModel?.name}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            {activeModel?.id === "yolov8" &&
              "Fast and accurate model suitable for real-time applications."}
            {activeModel?.id === "yolov10" &&
              "Latest YOLO version with improved accuracy and speed."}
            {activeModel?.id === "fasterrcnn" &&
              "High-precision model ideal for critical applications."}
            {activeModel?.id === "custom" &&
              "Load your own trained model for specific use cases."}
          </p>
        </div>
      </div>
    </div>
  );
}
