# Quick Start: Advanced Crowd Analysis

## Installation

### Step 1: Install PedPy Dependencies

Run the installation script:

```bash
cd "d:\College\Major Project"
install_pedpy.bat
```

OR manually install:

```bash
cd backend
pip install pedpy>=1.0.0 pandas>=1.3.0 scipy>=1.7.0
```

### Step 2: Start the System

**Backend:**

```bash
cd backend
python run.py
```

**Frontend:**

```bash
cd frontend
npm start
```

## Usage

### Webcam Mode

1. Open browser: `http://localhost:3000`
2. Go to **Webcam Counter** page
3. Select **YOLO model** (nano/small/medium/large)
4. ✅ Enable **"Enable Tracking (YOLO only)"**
5. Click **"Start Streaming"**
6. Wait 5-10 seconds for tracking data to accumulate
7. **Advanced metrics panel** appears automatically!

### External Camera Mode

1. Go to **External Camera** page
2. Enter IP camera URL (e.g., `rtsp://...` or `http://...`)
3. Select **YOLO model**
4. ✅ Enable **"Enable Tracking"**
5. Click **"Start Streaming"**
6. Advanced metrics appear in camera viewer

## What You'll See

### Advanced Crowd Analysis Panel

Beautiful purple gradient panel with:

**📊 Density Metrics** (3 types):

- **Classic Density**: Traditional counting-based density (ped/m²)
- **Voronoi Density**: Spatial tessellation density (ped/m²)
- **Voronoi (Cutoff)**: Voronoi with 12m radius limit (ped/m²)

**🚶 Speed Metrics** (2-4 types):

- **Mean Speed**: Average speed of all pedestrians (m/s)
- **Voronoi Speed**: Voronoi-weighted speed (m/s)
- **Mean Speed (Dir)**: Speed in movement direction (m/s) _if available_
- **Voronoi Speed (Dir)**: Voronoi directional speed (m/s) _if available_

### Example Values

```
Classic Density: 0.0456 ped/m²
Voronoi Density: 0.0523 ped/m²
Voronoi (Cutoff): 0.0489 ped/m²

Mean Speed: 1.234 m/s
Voronoi Speed: 1.156 m/s
```

## Troubleshooting

### Metrics not showing?

**Checklist**:

- ✅ Is **tracking enabled**? (checkbox checked)
- ✅ Is **YOLO model selected**? (not CSRNet/TMTB)
- ✅ Is **streaming active**?
- ✅ Are **tracks detected**? (check "Active Tracks" table below)
- ✅ Has **enough time passed**? (wait 5-10 seconds)

### Still 0.0000 values?

**Cause**: Not enough trajectory data yet
**Solution**:

- Move in front of camera
- Wait for "Frames Tracked" to increase
- Ensure consistent tracking (same track IDs across frames)

### Import errors?

**Error**: `Import "pedpy" could not be resolved`
**Solution**: Run `install_pedpy.bat` or manually install:

```bash
pip install pedpy pandas scipy
```

### Backend warnings?

**Warning**: `PedPy not installed. Cannot export trajectory data.`
**Solution**: Install PedPy (see above)

**Warning**: `Advanced metrics error: ...`
**Check**: Backend logs for detailed error
**Common causes**:

- Not enough tracking data (need multiple frames)
- No active tracks
- DataFrame conversion issue

## Advanced Features

### Understanding the Metrics

**Density Methods**:

1. **Classic**: Counts pedestrians in measurement area, divides by area

   - Fast, simple, traditional approach
   - Less accurate in dense crowds

2. **Voronoi**: Creates Voronoi tessellation around each pedestrian

   - More accurate representation of personal space
   - Better for varying crowd densities

3. **Voronoi with Cutoff**: Limits Voronoi cells to 12m radius
   - Prevents unrealistic large cells at edges
   - Most realistic for real-world scenarios

**Speed Methods**:

1. **Mean Speed**: Simple average of all pedestrian speeds

   - Easy to interpret
   - May be affected by outliers

2. **Voronoi Speed**: Weighted by Voronoi cell area

   - Gives more weight to isolated pedestrians
   - Better represents flow in heterogeneous crowds

3. **Directional Speeds**: Speed in specific movement direction
   - Useful for analyzing flow patterns
   - Currently optional (direction auto-detected if available)

### When to Use Each Metric

**Low Crowd Density** (<0.1 ped/m²):

- All metrics similar
- Use Classic for simplicity

**Medium Density** (0.1-0.5 ped/m²):

- Voronoi methods more accurate
- Use Voronoi with Cutoff for best results

**High Density** (>0.5 ped/m²):

- Voronoi Cutoff essential
- Classic may underestimate
- Speed metrics most reliable

### Real-World Interpretation

**Density Ranges**:

- `< 0.1 ped/m²`: Sparse crowd (free movement)
- `0.1-0.5 ped/m²`: Moderate crowd (some interaction)
- `0.5-2.0 ped/m²`: Dense crowd (constrained movement)
- `> 2.0 ped/m²`: Very dense (safety concerns)

**Speed Ranges**:

- `< 0.5 m/s`: Slow (standing/queuing)
- `0.5-1.5 m/s`: Normal walking
- `1.5-2.5 m/s`: Fast walking
- `> 2.5 m/s`: Running

## Tips for Best Results

### 1. Camera Setup

- **Height**: Mount camera 2-3 meters above ground
- **Angle**: Slightly tilted down (30-45°)
- **Coverage**: Ensure full area of interest visible
- **Lighting**: Good, consistent lighting

### 2. Tracking Settings

- **Model**: Start with YOLO-nano for speed
- **Upgrade**: Use YOLO-small/medium for better accuracy
- **Frame rate**: 30 fps recommended
- **Wait time**: Allow 10-15 seconds for stable metrics

### 3. Interpreting Results

- **First few seconds**: Metrics may fluctuate (warming up)
- **Stable phase**: After 10+ seconds, metrics stabilize
- **Track count**: More tracks = more reliable metrics
- **Unique count**: Should match approximate people in frame

### 4. Performance

- **CPU**: YOLO-nano fastest (real-time on most CPUs)
- **GPU**: Any YOLO variant real-time with CUDA
- **Latency**: ~50-100ms additional for PedPy calculations
- **Memory**: +200-500MB for trajectory storage

## What's Next?

### Coming Soon

- 📈 **Trajectory Plots**: Time-series visualization
- 🎨 **Density Heatmaps**: Spatial density overlay
- 🎯 **Custom Areas**: Click-to-define measurement zones
- 💾 **Export Data**: CSV download of trajectories
- 📊 **Historical Analysis**: Compare across time periods

### Feedback

Found a bug or have a suggestion?

- Check backend logs: `backend/logs/`
- Check browser console: F12 → Console tab
- Review implementation guide: `docs/version/v3/ADVANCED_CROWD_ANALYSIS_GUIDE.md`

## Support

### Documentation

- **Implementation**: `docs/version/v3/ADVANCED_CROWD_ANALYSIS_IMPLEMENTATION.md`
- **Guide**: `docs/version/v3/ADVANCED_CROWD_ANALYSIS_GUIDE.md`
- **PedPy Docs**: https://pedpy.readthedocs.io/

### Code References

- **Backend**: `ml/src/models/unified_counter.py` (lines 343-625)
- **Frontend**: `frontend/src/components/AdvancedMetrics.js`
- **WebSocket**: `backend/app/main.py` (lines 295-320, 495-520)

### Example Project

See original implementation:

- `ml/src/v3Updates/CrowdAnalyzer.py`
- Desktop GUI version with matplotlib plots

---

**Enjoy analyzing crowds scientifically! 🎉**
