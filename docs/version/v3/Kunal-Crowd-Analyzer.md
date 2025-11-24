# Kunal Crowd Analyzer

## Interface Overview

### Main Window
- **Video Display**: Shows the current video frame with tracking visualizations
- **Control Panel**: Contains buttons for loading videos, starting analysis, and accessing settings
- **Status Bar**: Displays current operation status and frame information

### Settings Window
- **Model Selection**: Choose between different YOLO models and tracking algorithms
- **Detection Parameters**: Adjust confidence and IOU thresholds
- **Output Configuration**: Set output paths and file naming conventions

## Loading and Processing Videos

### Basic Video Processing
1. Click "Load Video" and select your video file
2. Adjust the frame step if needed (higher values process fewer frames, improving performance)
3. Click "Start Processing" to begin analysis

### Calibration (First-Time Setup)
1. After loading a video, you'll be prompted to set up the scene
2. Click on four points in the video to define the ground plane
3. Enter the real-world distances between these points
4. The system will calculate the homography matrix for accurate measurements

## Analyzing Results

### Real-time Tracking
- Tracked objects are displayed with unique colors and IDs
- Trajectories are shown as paths behind moving objects
- Object speed is indicated by color (red = faster, blue = slower)

### Density Analysis
- View real-time density heatmaps
- Adjust the measurement area using the interactive controls
- Toggle between different density calculation methods

### Speed Analysis
- Monitor individual and average speeds
- Set speed thresholds for alerts
- Analyze speed distributions across different zones

## Exporting Data

### Export Options
- **Trajectory Data**: Save individual object trajectories as CSV
- **Density Maps**: Export density heatmaps as images or video
- **Analysis Reports**: Generate PDF reports with key metrics and visualizations

### Export Formats
- CSV: For further analysis in spreadsheet software
- JSON: For programmatic processing
- Video: Annotated video with tracking and analysis overlay

## Advanced Features

### Zone Definition
1. Click on "Define Zones" in the interface
2. Draw polygons to define areas of interest (e.g., crosswalks, waiting areas)
3. Set zone properties (name, type, alert thresholds)

### Batch Processing
- Create a text file listing paths to multiple videos
- Use the batch processing mode to analyze all videos sequentially
- Results are saved in separate folders for each video

### Custom Analysis Scripts
- The application provides a Python API for custom analysis
- Example scripts are available in the `examples/` directory

---

# Technical Architecture

## Libraries and Dependencies

### Core Libraries
- **PyTorch**: Deep learning framework for YOLO model implementation
- **OpenCV (cv2)**: Computer vision operations and video processing
- **NumPy**: Numerical computing and array operations
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Data visualization and plotting
- **SciPy**: Scientific computing and optimization
- **FilterPy**: Kalman filtering and tracking algorithms
- **Ultralytics YOLO**: Pre-trained YOLO models for object detection
- **PedPy**: Pedestrian dynamics analysis and visualization

### GUI and Utilities
- **PyQt6**: Cross-platform GUI framework
- **python-dotenv**: Environment variable management
- **tqdm**: Progress bars for long-running operations

### Optional/Integration
- **Groq Python Client**: For AI-powered plot interpretation
- **scikit-learn**: Machine learning utilities (if advanced analysis is needed)

## System Overview
Crowd Analyzer is built using a modular architecture that separates concerns into distinct components, enabling flexibility and maintainability. The system is designed to process video streams in real-time, perform complex computer vision tasks, and provide interactive visualization of results.

```
┌───────────────────────────────────────────────────────────────┐
│                      Crowd Analyzer                           │
├───────────────┬───────────────────────┬──────────────────────┤
│  Video Input  │  Core Processing     │  Analysis & Output   │
│  ┌─────────┐  │  ┌───────────────┐   │  ┌─────────────────┐ │
│  │  Video  │  │  │  Object       │   │  │  Density        │ │
│  │  Loader │──┼─▶│  Detection    │───┼─▶│  Analysis       │ │
│  └─────────┘  │  │  (YOLO)       │   │  │                 │ │
│               │  └───────┬───────┘   │  └─────────────────┘ │
│  ┌─────────┐  │  ┌───────▼───────┐   │  ┌─────────────────┐ │
│  │  Camera │  │  │  Object      │   │  │  Speed          │ │
│  │  Input  │──┼─▶│  Tracking    │───┼─▶│  Analysis       │ │
│  └─────────┘  │  │  (Kalman)    │   │  │                 │ │
│               │  └───────┬───────┘   │  └─────────────────┘ │
│  ┌─────────┐  │  ┌───────▼───────┐   │  ┌─────────────────┐ │
│  │  Batch  │  │  │  Trajectory  │   │  │  Visualization  │ │
│  │  Input  │──┼─▶│  Processing  │───┼─▶│  & Reporting    │ │
│  └─────────┘  │  │              │   │  │                 │ │
│               │  └───────────────┘   │  └─────────────────┘ │
└───────────────┴───────────────────────┴──────────────────────┘
```

## Core Components

### 1. Video Input Module
- **Video Loader**: Handles loading of video files from disk
- **Camera Interface**: Supports live camera input
- **Frame Buffer**: Manages frame queue for efficient processing

### 2. Object Detection (YOLO)
- **Model Management**: Handles loading and running YOLO models
- **Pre-processing**: Image normalization and resizing
- **Post-processing**: Non-maximum suppression and confidence filtering

### 3. Object Tracking
- **Kalman Filter**: Predicts object positions between frames
- **Hungarian Algorithm**: Associates detections with existing tracks
- **Track Management**: Handles track creation, update, and deletion

### 4. Trajectory Analysis
- **Coordinate Transformation**: Converts image coordinates to real-world coordinates
- **Trajectory Smoothing**: Applies filtering to reduce noise
- **Feature Extraction**: Calculates speed, direction, and other metrics

### 5. Density Analysis
- **Voronoi Diagrams**: Calculates personal space for each pedestrian
- **Classic Density**: Simple counting-based density estimation
- **Heatmap Generation**: Visualizes density distribution

### 6. Speed Analysis
- **Instantaneous Speed**: Frame-to-frame speed calculation
- **Average Speed**: Smoothed speed over time
- **Speed Distribution**: Statistical analysis of speed patterns

### 7. Visualization
- **OpenCV Drawing**: Real-time visualization of tracking and analysis
- **Matplotlib Plots**: Detailed plots and graphs
- **Interactive Controls**: User interface for analysis control

## Data Flow

### Input Stage
- Video frames are read from the source (file or camera)
- Frames are pre-processed (resize, normalize)

### Detection Stage
- YOLO model processes frames to detect objects
- Detections are filtered by confidence and class

### Tracking Stage
- Detections are associated with existing tracks
- New tracks are created for unassociated detections
- Tracks are updated with new measurements

### Analysis Stage
- Trajectories are processed to extract features
- Density and speed calculations are performed
- Results are aggregated over time

### Output Stage
- Results are visualized in real-time
- Data is saved to disk in various formats
- Reports and statistics are generated

## Performance Considerations

### Optimizations
- **GPU Acceleration**: Leverages CUDA for YOLO inference
- **Frame Skipping**: Processes every N-th frame for better performance
- **Multi-threading**: Separate threads for I/O, processing, and visualization

### Resource Management
- **Memory**: Implements frame buffering to control memory usage
- **CPU/GPU**: Balances workload between CPU and GPU
- **I/O**: Asynchronous file operations for efficient data handling

## Integration Points

### External Services
- **Groq API**: For AI-powered plot interpretation
- **Cloud Storage**: Optional integration with cloud providers
- **Analytics**: Export to third-party analysis tools

### Extensibility
- **Plugin System**: For adding new analysis modules
- **API**: For integration with other applications
- **Scripting**: Support for custom analysis scripts

## Security Considerations
- **Data Privacy**: Local processing of video data
- **Authentication**: For cloud service integration
- **Access Control**: For multi-user environments

## Future Enhancements
- **3D Analysis**: Support for depth-aware tracking
- **Behavior Analysis**: Anomaly detection and behavior classification
- **Mobile Support**: Lightweight version for mobile devices
- **Edge Deployment**: Optimized for edge computing devices
