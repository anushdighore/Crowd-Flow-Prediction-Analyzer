# Advanced Crowd Analysis Implementation Guide

## Overview

To implement the advanced outputs shown in `ml/src/v3Updates/CrowdAnalyzer.py`, we need to add:

1. **Density Estimation**

   - Classic density (people per square meter)
   - Voronoi density (spatial tessellation)
   - Voronoi with cutoff (limited Voronoi cells)

2. **Speed Analysis**

   - Individual speed calculation
   - Mean speed per frame
   - Direction-based speed
   - Voronoi speed

3. **Trajectory Analysis**

   - Full trajectory plots
   - Walkable area definition
   - Measurement area zones

4. **Advanced Visualizations**
   - Density over time plots
   - Speed over time plots
   - Trajectory path plots

## Backend Changes Required

### 1. Install PedPy Library

```bash
pip install pedpy
```

### 2. Update UnifiedCounter (ml/src/models/unified_counter.py)

Add these imports:

```python
from pedpy import (
    TrajectoryData, plot_trajectories, WalkableArea, MeasurementArea,
    compute_classic_density, compute_individual_voronoi_polygons,
    compute_voronoi_density, Cutoff, SpeedCalculation,
    compute_individual_speed, compute_mean_speed_per_frame,
    compute_voronoi_speed
)
import pandas as pd
```

Add methods for density and speed calculation:

```python
def calculate_density_metrics(self, trajectory_data, walkable_area, measurement_area):
    """
    Calculate different density metrics using PedPy

    Returns:
        dict with classic_density, voronoi_density, voronoi_density_cutoff
    """
    classic_density = compute_classic_density(
        traj_data=trajectory_data,
        measurement_area=measurement_area
    )

    individual = compute_individual_voronoi_polygons(
        traj_data=trajectory_data,
        walkable_area=walkable_area
    )

    density_voronoi, intersecting = compute_voronoi_density(
        individual_voronoi_data=individual,
        measurement_area=measurement_area
    )

    individual_cutoff = compute_individual_voronoi_polygons(
        traj_data=trajectory_data,
        walkable_area=walkable_area,
        cut_off=Cutoff(radius=12.0, quad_segments=1)
    )

    density_voronoi_cutoff, _ = compute_voronoi_density(
        individual_voronoi_data=individual_cutoff,
        measurement_area=measurement_area
    )

    return {
        'classic_density': classic_density,
        'voronoi_density': density_voronoi,
        'voronoi_density_cutoff': density_voronoi_cutoff,
        'voronoi_polygons': individual,
        'intersecting': intersecting
    }

def calculate_speed_metrics(self, trajectory_data, measurement_area, intersecting, frame_step=25):
    """
    Calculate different speed metrics using PedPy

    Returns:
        dict with mean_speed, voronoi_speed, directional_speed
    """
    # Individual speed (single-sided border)
    individual_speed = compute_individual_speed(
        traj_data=trajectory_data,
        frame_step=frame_step,
        compute_velocity=True,
        speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED
    )

    # Mean speed per frame
    mean_speed = compute_mean_speed_per_frame(
        traj_data=trajectory_data,
        measurement_area=measurement_area,
        individual_speed=individual_speed
    )

    # Voronoi-based speed
    voronoi_speed = compute_voronoi_speed(
        traj_data=trajectory_data,
        individual_voronoi_intersection=intersecting,
        individual_speed=individual_speed,
        measurement_area=measurement_area
    )

    # Direction-based speed (assuming downward movement)
    individual_speed_direction = compute_individual_speed(
        traj_data=trajectory_data,
        frame_step=5,
        movement_direction=np.array([0, -1]),
        compute_velocity=True,
        speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED
    )

    mean_speed_direction = compute_mean_speed_per_frame(
        traj_data=trajectory_data,
        measurement_area=measurement_area,
        individual_speed=individual_speed_direction
    )

    voronoi_speed_direction = compute_voronoi_speed(
        traj_data=trajectory_data,
        individual_voronoi_intersection=intersecting,
        individual_speed=individual_speed_direction,
        measurement_area=measurement_area
    )

    return {
        'mean_speed': mean_speed,
        'voronoi_speed': voronoi_speed,
        'mean_speed_direction': mean_speed_direction,
        'voronoi_speed_direction': voronoi_speed_direction
    }

def export_trajectory_data(self, frame_rate=30):
    """
    Export trajectory data for PedPy analysis

    Returns:
        TrajectoryData object
    """
    if not self.track_history:
        return None

    # Convert track history to DataFrame format for PedPy
    rows = []
    for track_id, positions in self.track_history.items():
        for frame_idx, (x, y) in enumerate(positions):
            rows.append({
                'id': track_id,
                'frame': frame_idx,
                'x': x,
                'y': y
            })

    df = pd.DataFrame(rows)
    traj_data = TrajectoryData(data=df, frame_rate=frame_rate)

    return traj_data
```

### 3. Update WebSocket Endpoints

Modify `/ws/count` and `/ws/external-camera` to include advanced metrics:

```python
# After getting tracking results
if enable_tracking and len(tracks) > 0:
    # Export trajectory data
    traj_data = counter.export_trajectory_data(frame_rate=30)

    if traj_data is not None:
        # Define walkable and measurement areas (can be configurable)
        walkable_area = WalkableArea(polygon=np.array([
            [0, 0],
            [frame.shape[1], 0],
            [frame.shape[1], frame.shape[0]],
            [0, frame.shape[0]]
        ]))

        measurement_area = MeasurementArea(polygon=np.array([
            [0, 0],
            [frame.shape[1], 0],
            [frame.shape[1], frame.shape[0]],
            [0, frame.shape[0]]
        ]))

        # Calculate metrics
        density_metrics = counter.calculate_density_metrics(
            traj_data, walkable_area, measurement_area
        )

        speed_metrics = counter.calculate_speed_metrics(
            traj_data, measurement_area,
            density_metrics['intersecting']
        )

        # Add to response
        response_data['density_metrics'] = {
            'classic_density': density_metrics['classic_density'].iloc[-1] if len(density_metrics['classic_density']) > 0 else 0,
            'voronoi_density': density_metrics['voronoi_density'].iloc[-1] if len(density_metrics['voronoi_density']) > 0 else 0,
            'voronoi_density_cutoff': density_metrics['voronoi_density_cutoff'].iloc[-1] if len(density_metrics['voronoi_density_cutoff']) > 0 else 0
        }

        response_data['speed_metrics'] = {
            'mean_speed': speed_metrics['mean_speed'].iloc[-1] if len(speed_metrics['mean_speed']) > 0 else 0,
            'voronoi_speed': speed_metrics['voronoi_speed'].iloc[-1] if len(speed_metrics['voronoi_speed']) > 0 else 0,
            'mean_speed_direction': speed_metrics['mean_speed_direction'].iloc[-1] if len(speed_metrics['mean_speed_direction']) > 0 else 0,
            'voronoi_speed_direction': speed_metrics['voronoi_speed_direction'].iloc[-1] if len(speed_metrics['voronoi_speed_direction']) > 0 else 0
        }
```

## Frontend Changes Required

### 1. Create Advanced Metrics Display Component

Create `frontend/src/components/AdvancedMetrics.js`:

```javascript
import React from "react";

export default function AdvancedMetrics({ densityMetrics, speedMetrics }) {
  if (!densityMetrics && !speedMetrics) return null;

  return (
    <div className="advanced-metrics">
      <h4>📊 Advanced Crowd Analysis</h4>

      {densityMetrics && (
        <div className="metrics-group">
          <h5>🏘️ Density Metrics (people/m²)</h5>
          <div className="metric-row">
            <span className="metric-label">Classic Density:</span>
            <span className="metric-value">
              {densityMetrics.classic_density?.toFixed(3)}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Voronoi Density:</span>
            <span className="metric-value">
              {densityMetrics.voronoi_density?.toFixed(3)}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Voronoi (Cutoff):</span>
            <span className="metric-value">
              {densityMetrics.voronoi_density_cutoff?.toFixed(3)}
            </span>
          </div>
        </div>
      )}

      {speedMetrics && (
        <div className="metrics-group">
          <h5>🚶 Speed Metrics (m/s)</h5>
          <div className="metric-row">
            <span className="metric-label">Mean Speed:</span>
            <span className="metric-value">
              {speedMetrics.mean_speed?.toFixed(3)}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Voronoi Speed:</span>
            <span className="metric-value">
              {speedMetrics.voronoi_speed?.toFixed(3)}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Directional Speed:</span>
            <span className="metric-value">
              {speedMetrics.mean_speed_direction?.toFixed(3)}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Voronoi (Directional):</span>
            <span className="metric-value">
              {speedMetrics.voronoi_speed_direction?.toFixed(3)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 2. Update WebcamCounter.js

Add to the statistics panel:

```javascript
import AdvancedMetrics from "./components/AdvancedMetrics";

// In the stats section:
{
  enableTracking && results && (
    <AdvancedMetrics
      densityMetrics={results.density_metrics}
      speedMetrics={results.speed_metrics}
    />
  );
}
```

### 3. Create Trajectory Plot Visualizer

Create `frontend/src/components/TrajectoryPlot.js`:

```javascript
import React, { useEffect, useRef } from "react";

export default function TrajectoryPlot({
  trajectoryData,
  width = 600,
  height = 400,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!trajectoryData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = "#f5f5f5";
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = "#e0e0e0";
    ctx.lineWidth = 1;
    for (let i = 0; i < width; i += 50) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, height);
      ctx.stroke();
    }
    for (let j = 0; j < height; j += 50) {
      ctx.beginPath();
      ctx.moveTo(0, j);
      ctx.lineTo(width, j);
      ctx.stroke();
    }

    // Draw trajectories
    const colors = [
      "#667eea",
      "#764ba2",
      "#f093fb",
      "#4facfe",
      "#00f2fe",
      "#43e97b",
      "#fa709a",
      "#fee140",
    ];

    Object.entries(trajectoryData).forEach(([trackId, positions], idx) => {
      const color = colors[idx % colors.length];

      if (positions.length < 2) return;

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      positions.forEach((pos, i) => {
        const x = (pos.x / trajectoryData.maxX) * width;
        const y = (pos.y / trajectoryData.maxY) * height;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();

      // Draw start point
      const startX = (positions[0].x / trajectoryData.maxX) * width;
      const startY = (positions[0].y / trajectoryData.maxY) * height;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(startX, startY, 5, 0, 2 * Math.PI);
      ctx.fill();

      // Draw end point
      const endX =
        (positions[positions.length - 1].x / trajectoryData.maxX) * width;
      const endY =
        (positions[positions.length - 1].y / trajectoryData.maxY) * height;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(endX, endY, 5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }, [trajectoryData, width, height]);

  return (
    <div className="trajectory-plot">
      <h4>🛤️ Pedestrian Trajectories</h4>
      <canvas ref={canvasRef} width={width} height={height} />
    </div>
  );
}
```

## Implementation Steps

1. **Backend**:

   - Install pedpy: `pip install pedpy`
   - Update `unified_counter.py` with density/speed calculation methods
   - Modify WebSocket endpoints to include advanced metrics

2. **Frontend**:

   - Create `AdvancedMetrics.js` component
   - Create `TrajectoryPlot.js` component
   - Update WebcamCounter, ExternalCam, VideoUploader to display advanced metrics

3. **Configuration**:
   - Add walkable area configuration
   - Add measurement area configuration
   - Add frame rate settings
   - Add frame step settings

Would you like me to implement these changes step by step?
