import { useState } from "react";
import { Upload, Image, Video, X } from "lucide-react";

type MediaType = "image" | "video" | null;

export default function MediaUploadCard() {
  const [activeTab, setActiveTab] = useState<MediaType>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileSelect = (file: File | null, type: MediaType) => {
    if (file) {
      setUploadedFile(file);
      setActiveTab(type);
    }
  };

  const handleClearFile = () => {
    setUploadedFile(null);
    setActiveTab(null);
  };

  const handleDrop = (e: React.DragEvent, type: MediaType) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0], type);
    }
  };

  return (
    <div className="relative p-6 rounded-xl border border-neon-cyan/20 bg-gradient-to-br from-card to-background overflow-hidden group hover:border-neon-cyan/50 transition-all duration-300">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-neon-cyan/10">
            <Upload className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">Media Upload</h3>
        </div>

        {/* Tabs */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setActiveTab("image")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === "image"
                ? "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50"
                : "bg-background border border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            <Image className="w-4 h-4" />
            Image
          </button>
          <button
            onClick={() => setActiveTab("video")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === "video"
                ? "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50"
                : "bg-background border border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            <Video className="w-4 h-4" />
            Video
          </button>
        </div>

        {/* Upload Area */}
        {!uploadedFile ? (
          <div
            onDrop={(e) => handleDrop(e, activeTab || "image")}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-neon-cyan/30 rounded-lg p-8 text-center hover:border-neon-cyan/50 transition-colors cursor-pointer"
          >
            <label className="flex flex-col items-center justify-center gap-3 cursor-pointer">
              <div className="p-3 rounded-lg bg-neon-cyan/10">
                {activeTab === "video" ? (
                  <Video className="w-6 h-6 text-neon-cyan" />
                ) : (
                  <Image className="w-6 h-6 text-neon-cyan" />
                )}
              </div>
              <div>
                <p className="font-semibold text-foreground text-sm">
                  Drop {activeTab || "file"} or click to upload
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {activeTab === "video"
                    ? "MP4, AVI, MOV up to 1GB"
                    : "JPG, PNG up to 50MB"}
                </p>
              </div>
              <input
                type="file"
                accept={
                  activeTab === "video" ? "video/*" : "image/*"
                }
                onChange={(e) =>
                  handleFileSelect(
                    e.target.files?.[0] || null,
                    activeTab || "image"
                  )
                }
                className="hidden"
              />
            </label>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30 flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                {activeTab === "video" ? (
                  <Video className="w-5 h-5 text-neon-cyan flex-shrink-0 mt-0.5" />
                ) : (
                  <Image className="w-5 h-5 text-neon-cyan flex-shrink-0 mt-0.5" />
                )}
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate">
                    {uploadedFile.name}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={handleClearFile}
                className="p-1 hover:bg-neon-cyan/20 rounded transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            <button className="w-full relative px-4 py-2 font-medium text-background rounded-lg overflow-hidden group/btn">
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue" />
              <span className="relative">Process {activeTab}</span>
            </button>

            <button
              onClick={handleClearFile}
              className="w-full px-4 py-2 font-medium text-foreground border border-neon-cyan/30 rounded-lg hover:bg-neon-cyan/5 transition-colors text-sm"
            >
              Clear & Upload New
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
