# ExternalCam Modularization - Developer Guide

## What Changed?

The **ExternalCam.js component** was a massive 741-line monolith with ALL functionality crammed into one file.

**Now it's broken into 8 focused, reusable components:**

```
Components/Camera/
├── ExternalCam.js (Main orchestrator)
├── CameraControls.js (User inputs)
├── SettingsPanel.js (Toggles)
├── CameraDisplay.js (Camera feed)
├── HeatmapDisplay.js (Heatmap view)
├── StreamStats.js (Statistics)
├── TrackingDetails.js (Track info)
└── AnalyticsGraphs.js (Graphs)
```

---

## Usage Guide

### Basic Import

```javascript
import ExternalCam from "../components/Camera/ExternalCam";

// Use as a complete, self-contained component
<ExternalCam />;
```

### Using Individual Components

```javascript
import CameraControls from "../components/Camera/CameraControls";
import StreamStats from "../components/Camera/StreamStats";

// In your component
<CameraControls
  cameraUrl={url}
  onCameraUrlChange={setUrl}
  // ... other props
/>;
```

---

## Component Reference

### ExternalCam.js

**The brain** - Manages all state and WebSocket logic

```javascript
<ExternalCam />

// No props needed - it's completely self-contained
```

**Internal State**:

- `cameraUrl` - Camera stream URL
- `isStreaming` - Stream active flag
- `selectedModel` - Selected ML model
- `results` - Latest predictions
- `countHistory` - Array of count data points
- `fpsHistory` - Array of FPS data points
- `enableHeatmap` - Heatmap toggle
- `enableTracking` - Tracking toggle
- `autoSwitch` - Auto-model-switch flag

---

### CameraControls.js

**Input component** - Camera setup and control buttons

```javascript
<CameraControls
  cameraUrl="http://..."
  onCameraUrlChange={(url) => setCameraUrl(url)}
  selectedModel="yolo-nano"
  onModelChange={(model) => setSelectedModel(model)}
  autoSwitch={false}
  onAutoSwitchChange={(val) => setAutoSwitch(val)}
  autoSwitchThreshold={30}
  onThresholdChange={(val) => setThreshold(val)}
  isStreaming={false}
  loading={false}
  error={null}
  onTestConnection={() => testCam()}
  onStartStream={() => start()}
  onStopStream={() => stop()}
  showSettings={false}
  onShowSettings={() => toggle()}
/>
```

---

### SettingsPanel.js

**Toggle component** - Visualization settings

```javascript
<SettingsPanel
  enableHeatmap={true}
  onEnableHeatmapChange={(val) => setHeatmap(val)}
  enableTracking={true}
  onEnableTrackingChange={(val) => setTracking(val)}
  isStreaming={false}
/>
```

---

### CameraDisplay.js

**Display component** - Live camera feed with overlays

```javascript
<CameraDisplay
  imgRef={imgRef} // ref for image element
  results={results} // Latest predictions
  enableTracking={true} // Show trajectory
  autoSwitch={false} // Show auto-switch badge
  currentAutoModel="yolo-nano" // Current model
/>
```

---

### HeatmapDisplay.js

**Display component** - Heatmap overlay

```javascript
<HeatmapDisplay
  heatmapImage={results?.heatmap} // Base64 heatmap
  enableHeatmap={true} // Show toggle
  selectedModel="csrnet" // Model type
  heatmapRef={heatmapRef} // ref for heatmap
/>
```

---

### StreamStats.js

**Stats component** - Performance and count statistics

```javascript
<StreamStats
  results={results} // Prediction results
  enableTracking={true} // Debug info visibility
  fps={30.5} // Frames per second
  frameCount={150} // Total frames
  autoSwitch={false} // Show indicator
  autoSwitchThreshold={30} // Threshold value
  currentAutoModel="yolo-nano" // Current model
/>
```

---

### TrackingDetails.js

**Stats component** - Track information table

```javascript
<TrackingDetails
  results={results} // Must have results.tracks array
  enableTracking={true} // When false, renders nothing
/>
```

---

### AnalyticsGraphs.js

**Chart component** - Real-time trend graphs

```javascript
<AnalyticsGraphs
  countHistory={[
    { time: Date.now(), count: 15 },
    { time: Date.now() + 200, count: 16 },
    // ...
  ]}
  fpsHistory={[
    { time: Date.now(), fps: 30.5 },
    // ...
  ]}
  enableTracking={true} // Show advanced metrics
  results={results} // For advanced metrics
/>
```

---

## Code Structure

### ExternalCam.js Structure

```javascript
export default function ExternalCam() {
  // 1. STATE MANAGEMENT
  const [cameraUrl, setCameraUrl] = useState("...");
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedModel, setSelectedModel] = useState("yolo-nano");
  // ... more state

  // 2. REFS
  const imgRef = useRef(null);
  const heatmapRef = useRef(null);
  const wsRef = useRef(null);

  // 3. UTILITY FUNCTIONS
  const disconnectWebSocket = useCallback(() => { ... });
  const stopStream = useCallback(() => { ... });
  const testConnection = async () => { ... };
  const connectWebSocket = useCallback(() => { ... });
  const requestFrame = useCallback(() => { ... });
  const startStream = useCallback(() => { ... });

  // 4. EFFECTS
  useEffect(() => { return () => stopStream(); }, [stopStream]);

  // 5. RENDER - Using modular components
  return (
    <div className="webcam-counter">
      <div className="container">
        <h1>🎥 External IP Camera with Crowd Counting</h1>

        <CameraControls {...controlProps} />
        {showSettings && <SettingsPanel {...settingsProps} />}

        {isStreaming && (
          <>
            <CameraDisplay {...displayProps} />
            <HeatmapDisplay {...heatmapProps} />
            <StreamStats {...statsProps} />
            <TrackingDetails {...trackingProps} />
            <AnalyticsGraphs {...analyticsProps} />
          </>
        )}

        <div className="info-panel">{ ... }</div>
      </div>
    </div>
  );
}
```

---

## Adding New Components

### Example: Add a Recording Component

```javascript
// 1. Create RecordingPanel.js
export default function RecordingPanel({
  isRecording,
  onStartRecording,
  onStopRecording,
  recordingTime,
}) {
  return (
    <div className="recording-panel">
      <h3>🎥 Recording</h3>
      <p>Status: {isRecording ? "Recording" : "Stopped"}</p>
      <p>Time: {recordingTime}s</p>
      <button onClick={onStartRecording}>Start</button>
      <button onClick={onStopRecording}>Stop</button>
    </div>
  );
}

// 2. Add state to ExternalCam.js
const [isRecording, setIsRecording] = useState(false);
const [recordingTime, setRecordingTime] = useState(0);

// 3. Add to render
<RecordingPanel
  isRecording={isRecording}
  onStartRecording={() => startRecording()}
  onStopRecording={() => stopRecording()}
  recordingTime={recordingTime}
/>;
```

---

## Data Flow Example

**User enters camera URL and clicks Start:**

```
1. User types URL in input
   → onCameraUrlChange fires
   → setCameraUrl(newUrl)
   → State updates

2. User clicks Start
   → onStartStream fires in ExternalCam
   → setIsStreaming(true)
   → connectWebSocket() called
   → WebSocket connects to backend

3. Backend sends frame data
   → ws.onmessage fires
   → setResults(data)
   → setFps(data.fps)
   → Updates all relevant arrays

4. State updates propagate
   → CameraDisplay re-renders with new frame
   → StreamStats re-renders with new fps
   → Graphs re-render with new history points
```

---

## Common Patterns

### Conditional Rendering

```javascript
// Show component only when streaming
{
  isStreaming && <CameraDisplay {...props} />;
}

// Show component only when tracking enabled
{
  enableTracking && results && <TrackingDetails {...props} />;
}

// Show component only when data available
{
  countHistory.length > 1 && <AnalyticsGraphs {...props} />;
}
```

### Prop Passing

```javascript
// Pass required data
<CameraDisplay imgRef={imgRef} results={results} />

// Pass callbacks
<CameraControls
  onCameraUrlChange={setCameraUrl}
  onStartStream={startStream}
/>

// Pass configuration
<StreamStats enableTracking={enableTracking} fps={fps} />
```

### State Management Pattern

```javascript
// In ExternalCam.js - the manager
const [value, setValue] = useState(initialValue);

// Pass to child
<ChildComponent
  value={value}
  onChange={setValue}
/>

// Child handles the event
<input onChange={(e) => onChange(e.target.value)} />
```

---

## Testing Examples

### Test a Component in Isolation

```javascript
// CameraControls.test.js
import CameraControls from "../CameraControls";
import { render, screen, fireEvent } from "@testing-library/react";

test("calls onStartStream when Start button clicked", () => {
  const mockStart = jest.fn();
  const mockTestConnection = jest.fn();

  render(
    <CameraControls
      isStreaming={false}
      onStartStream={mockStart}
      onTestConnection={mockTestConnection}
      // ... other props
    />
  );

  const startBtn = screen.getByText("▶️ Start Stream");
  fireEvent.click(startBtn);

  expect(mockStart).toHaveBeenCalled();
});
```

### Test Integration

```javascript
// ExternalCam.integration.test.js
test("ExternalCam orchestrates all components", () => {
  render(<ExternalCam />);

  // Should render all sub-components
  expect(screen.getByText("🎥 External IP Camera")).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/camera url/i)).toBeInTheDocument();
  expect(screen.getByText("🔍 Test Camera")).toBeInTheDocument();
});
```

---

## Performance Tips

1. **Use ref directly** for frequently updated elements (camera feed)
2. **Memoize callbacks** with useCallback to prevent child re-renders
3. **Conditional rendering** to skip rendering when not needed
4. **History array limits** - keep only last 50 points for graphs

---

## Troubleshooting

### "Component not rendering"

- Check if parent component is passing required props
- Verify state is being set correctly
- Check browser console for errors

### "WebSocket connection failed"

- Check backend is running on correct port
- Verify camera URL is accessible
- Check network tab for failed requests

### "Heatmap not showing"

- Verify `enableHeatmap` is true
- Check if backend returns heatmap data
- Ensure heatmapRef is properly passed

---

## File Locations

```
frontend/
└── src/
    ├── components/
    │   ├── Camera/
    │   │   ├── ExternalCam.js ✅
    │   │   ├── CameraControls.js ✅
    │   │   ├── SettingsPanel.js ✅
    │   │   ├── CameraDisplay.js ✅
    │   │   ├── HeatmapDisplay.js ✅
    │   │   ├── StreamStats.js ✅
    │   │   ├── TrackingDetails.js ✅
    │   │   └── AnalyticsGraphs.js ✅
    │   └── (other components)
    └── pages/
        └── ExternalCameraPage.js ✅
```

---

## Maintenance Checklist

- [ ] All components have JSDoc comments
- [ ] Props are typed/documented
- [ ] Error handling is complete
- [ ] Loading states are handled
- [ ] Refs are properly cleaned up on unmount
- [ ] Event handlers are properly bound
- [ ] No console warnings
- [ ] Mobile responsive CSS applied

---

**Happy Coding! 🎉**

For questions, check the component JSDoc comments or the architecture diagram.
