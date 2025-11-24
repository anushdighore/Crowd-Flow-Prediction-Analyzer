import React, { useState } from "react";
import Menu from "../Menu/Menu";
import Nav from "../Nav/Nav";
import RightMenu from "../Menu/RightMenu";
import "./Layout.css";

/**
 * Layout Component - 4-Part Global Layout
 * Part 1: Navigation (Top, Full Width)
 * Part 2: Menu/Sidebar (Left Column)
 * Part 3: Main Content (Center Column)
 * Part 4: Right Menu/Sidebar (Right Column - Fixed)
 */
function Layout({
  children,
  showRightMenu = true,
  selectedModel = "CSRNet",
  onModelChange,
  isStreaming = false,
  onStreamToggle,
  enableTracking = false,
  onTrackingChange,
  enableHeatmap = false,
  onHeatmapChange,
  detectionThreshold = 0.5,
  onThresholdChange,
}) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isRightMenuOpen, setIsRightMenuOpen] = useState(true);
  const [mode, setMode] = useState("dashboard");
  const [settings, setSettings] = useState({
    resolution: "high",
    autoMode: false,
    realtime: false,
    heatmap: true,
  });

  return (
    <div
      className="app-layout"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* PART 1: NAVIGATION BAR - TOP (Full Width) */}
      <div className="layout-nav-bar">
        <Nav mode={mode} setMode={setMode} />
      </div>

      {/* PART 2, 3 & 4: MAIN CONTAINER (Left Sidebar + Content + Right Menu) */}
      <div
        className="layout-main-container"
        style={{ display: "flex", flex: 1, overflow: "hidden" }}
      >
        {/* PART 2: SIDEBAR MENU (Left) */}
        <div className={`layout-sidebar ${isMenuOpen ? "menu-open" : ""}`}>
          <Menu
            isOpen={isMenuOpen}
            onClose={() => setIsMenuOpen(false)}
            onToggle={() => setIsMenuOpen(!isMenuOpen)}
          />
        </div>

        {/* PART 3: MAIN CONTENT AREA (Center) */}
        <main
          className="layout-content"
          style={{
            flex: 1,
            overflowY: "auto",
            paddingRight: isRightMenuOpen ? "320px" : "50px",
            transition: "all 0.3s ease",
          }}
        >
          {children}
        </main>

        {/* PART 4: RIGHT MENU (Right - Fixed) */}
        {showRightMenu && (
          <RightMenu
            isOpen={isRightMenuOpen}
            onToggle={setIsRightMenuOpen}
            selectedModel={selectedModel}
            onModelChange={onModelChange}
            settings={settings}
            onSettingsChange={setSettings}
            isStreaming={isStreaming}
            onStreamToggle={onStreamToggle}
            enableTracking={enableTracking}
            onTrackingChange={onTrackingChange}
            enableHeatmap={enableHeatmap}
            onHeatmapChange={onHeatmapChange}
            detectionThreshold={detectionThreshold}
            onThresholdChange={onThresholdChange}
          />
        )}
      </div>
    </div>
  );
}

export default Layout;
