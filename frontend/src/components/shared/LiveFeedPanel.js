import React from "react";

/**
 * LiveFeedPanel - Reusable component for displaying raw video/image feed
 * Used by both Webcam and External Camera pages
 */
const LiveFeedPanel = ({
  // For webcam (video element)
  videoRef,
  // For external camera (image element)
  imgRef,
  imageSrc,
  // Common props
  isStreaming,
  count,
  title = "📹 Live Feed",
  placeholderText = "Click Start to begin streaming",
  feedType = "video", // "video" or "image"
}) => {
  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        padding: "1.5rem",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <h3 style={{ margin: "0 0 1rem 0" }}>{title}</h3>
      <div
        style={{
          position: "relative",
          width: "100%",
          paddingBottom: "56.25%",
          background: "#000",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        {feedType === "video" ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        ) : (
          isStreaming && (
            <img
              ref={imgRef}
              src={imageSrc}
              alt="Camera feed"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                objectFit: "contain",
              }}
            />
          )
        )}

        {/* Count overlay */}
        {isStreaming && (
          <div
            style={{
              position: "absolute",
              top: "12px",
              left: "12px",
              background: "rgba(15,23,42,0.85)",
              color: "white",
              padding: "0.4rem 0.75rem",
              borderRadius: "8px",
              fontWeight: 600,
              letterSpacing: "0.05em",
              fontSize: "0.95rem",
              boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
            }}
          >
            Count: {Number.isFinite(count) ? count.toFixed(2) : "--"}
          </div>
        )}

        {/* Live indicator */}
        {isStreaming && (
          <div
            style={{
              position: "absolute",
              top: "12px",
              right: "12px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              background: "rgba(220,38,38,0.9)",
              color: "white",
              padding: "0.3rem 0.6rem",
              borderRadius: "4px",
              fontSize: "0.75rem",
              fontWeight: 600,
            }}
          >
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "white",
                animation: "pulse 1s infinite",
              }}
            />
            LIVE
          </div>
        )}

        {/* Placeholder when not streaming */}
        {!isStreaming && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              fontSize: "1.25rem",
              fontWeight: "600",
              textAlign: "center",
              padding: "1rem",
            }}
          >
            {placeholderText}
          </div>
        )}
      </div>

      {/* Add CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default LiveFeedPanel;
