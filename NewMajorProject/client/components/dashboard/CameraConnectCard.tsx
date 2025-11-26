import { useState } from "react";
import { Camera, CheckCircle, AlertCircle, Wifi } from "lucide-react";

export default function CameraConnectCard() {
  const [ipAddress, setIpAddress] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = () => {
    if (!ipAddress.trim()) return;
    setIsLoading(true);
    setTimeout(() => {
      setIsConnected(true);
      setIsLoading(false);
    }, 1500);
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setIpAddress("");
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
            <Camera className="w-6 h-6 text-neon-cyan" />
          </div>
          <h3 className="font-bold text-foreground">IP Camera Feed</h3>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 mb-6">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? "bg-green-500" : "bg-yellow-500"
            }`}
          />
          <span className="text-sm text-muted-foreground">
            {isConnected ? "Connected" : "Not Connected"}
          </span>
        </div>

        {/* Connection form */}
        {!isConnected ? (
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-muted-foreground mb-2 block">
                IP Address (IP Webcam App)
              </label>
              <input
                type="text"
                placeholder="192.168.1.100:8080"
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-input border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-neon-cyan/50 transition-all"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Enter IP address and port from IP Webcam app
              </p>
            </div>

            <button
              onClick={handleConnect}
              disabled={!ipAddress.trim() || isLoading}
              className="w-full relative px-4 py-2 font-medium text-background rounded-lg overflow-hidden group/btn disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover/btn:opacity-90 transition-opacity" />
              <span className="relative flex items-center justify-center gap-2">
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Wifi className="w-4 h-4" />
                    Connect Camera
                  </>
                )}
              </span>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-foreground">
                  Camera Connected
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {ipAddress}
                </p>
              </div>
            </div>

            <button
              onClick={handleDisconnect}
              className="w-full px-4 py-2 font-medium text-foreground border border-neon-cyan/30 rounded-lg hover:bg-neon-cyan/5 transition-colors text-sm"
            >
              Disconnect
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
