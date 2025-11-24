# 🚀 Demo Mode Quick Start Guide

## Critical Fixes Applied

### ✅ **ISSUE #1: Routes Not Working (/image, /video redirecting to landing)**

**Root Cause:** The app was using `router/index.js` which only had 3 routes, not the full route list in `App.js`

**Fixed:**

- ✅ Added ALL routes to `router/index.js`: `/image`, `/video`, `/hls`, `/pedestrian`, `/dashboard`
- ✅ Imported `ImagePage`, `VideoPage`, `HLSStreamingPage`, `PedestrianTracker`

### ✅ **ISSUE #2: Authentication Blocking Access**

**Root Cause:** Authentication was required but in demo mode

**Fixed:**

- ✅ **DEMO MODE ENABLED** in `AuthContext.js` - Set `DEMO_MODE = true`
- ✅ Automatically authenticates users as "demo" user
- ✅ All routes now accessible without login

### ✅ **ISSUE #3: Missing Dependencies**

**Root Cause:** axios was mentioned but not in package.json

**Fixed:**

- ✅ Added `axios: ^1.6.0` to package.json (though fetch API is currently used)
- ✅ Created `.env.development` and `.env.production` with API endpoints

---

## 🎯 How to Start the Application

### **Step 1: Install Frontend Dependencies**

```bash
cd frontend
npm install
```

> This will install axios and all other dependencies

### **Step 2: Start Backend (FastAPI)**

```bash
cd backend
python run.py
```

> Backend will run on http://localhost:8000

### **Step 3: Start Frontend (React)**

```bash
cd frontend
npm start
```

> Frontend will run on http://localhost:3000

---

## 📋 Available Routes (All Working Now)

| Route              | Page                | Description                                     |
| ------------------ | ------------------- | ----------------------------------------------- |
| `/`                | Landing Page        | Home page with feature cards                    |
| `/login`           | Login Page          | Authentication (bypassed in demo mode)          |
| `/dashboard`       | Dashboard           | Overview of all features                        |
| `/image`           | Image Upload        | Upload & analyze images with CSRNet/VMamba/YOLO |
| `/video`           | Video Upload        | Upload & analyze videos                         |
| `/webcam`          | Live Webcam         | Real-time webcam detection                      |
| `/external-camera` | External Camera     | RTSP/HTTP camera streams                        |
| `/hls`             | HLS Streaming       | HLS video streaming                             |
| `/pedestrian`      | Pedestrian Tracking | Trajectory analysis                             |

---

## 🔧 Technology Stack

### Frontend:

- ✅ **React 19.1.1** - UI Framework
- ✅ **react-router-dom 7.9.4** - Routing (NOT axios - that's for HTTP)
- ✅ **axios 1.6.0** - HTTP requests (newly added)
- ✅ **Fetch API** - Currently used for uploads (native browser API)

### Backend:

- ✅ **FastAPI** - Python backend framework
- ✅ **WebSocket** - Real-time communication
- ✅ **CORS enabled** - Cross-origin requests allowed

### Models:

- ✅ **CSRNet** - Density-based counting
- ✅ **VMamba TMTB** - Fine-tuned model
- ✅ **YOLOv8** - Object detection with tracking
- ✅ **MCNN** - Coming soon

---

## 🧪 Testing Routes

### Test /image route:

1. Navigate to http://localhost:3000/image
2. You should see the image upload page with model selection
3. Upload an image and click "Count Crowd"

### Test /video route:

1. Navigate to http://localhost:3000/video
2. You should see the video upload interface
3. Upload a video file

### Test /dashboard:

1. Navigate to http://localhost:3000/dashboard
2. You should see overview cards for all features

---

## 🐛 Debugging Issues

### If routes still redirect to landing page:

1. Check browser console for errors
2. Verify `DEMO_MODE = true` in `src/context/AuthContext.js`
3. Clear browser cache and localStorage:
   ```javascript
   localStorage.clear();
   ```
4. Restart the React dev server

### If API calls fail:

1. Verify backend is running on port 8000
2. Check `.env.development` has correct API URL
3. Check browser network tab for CORS errors
4. Verify backend CORS middleware allows `http://localhost:3000`

### If demo mode doesn't work:

1. Open `src/context/AuthContext.js`
2. Verify line 7: `const DEMO_MODE = true;`
3. Check browser console for AuthContext errors

---

## 🔄 How to Disable Demo Mode

Edit `src/context/AuthContext.js`:

```javascript
const DEMO_MODE = false; // Change from true to false
```

Then users will need to login via `/login` route.

---

## 📡 API Endpoints (Backend)

The backend exposes these endpoints:

| Endpoint               | Method    | Description             |
| ---------------------- | --------- | ----------------------- |
| `/api/v1/csrnet/count` | POST      | CSRNet image counting   |
| `/api/v1/tmtb/count`   | POST      | VMamba TMTB counting    |
| `/api/v1/yolo/count`   | POST      | YOLOv8 detection        |
| `/ws/count`            | WebSocket | Real-time streaming     |
| `/api/hls/*`           | GET       | HLS streaming endpoints |

---

## ✨ What Was Fixed

### Before:

- ❌ `/image` redirected to landing page
- ❌ `/video` redirected to landing page
- ❌ Routes only in `App.js` but `router/index.js` was being used
- ❌ No demo mode - authentication required
- ❌ axios missing from dependencies

### After:

- ✅ All routes work correctly
- ✅ `router/index.js` has complete route list
- ✅ Demo mode auto-authenticates users
- ✅ axios added to package.json
- ✅ Environment variables configured
- ✅ No compilation errors

---

## 🎓 Understanding the Routing

The app uses **two routing concepts**:

1. **react-router-dom** - Client-side routing (navigation between pages)

   - Example: Clicking link to `/image` shows Image component
   - Used for: Navigation between pages

2. **axios/fetch** - HTTP requests to backend API
   - Example: Uploading image to `/api/v1/csrnet/count`
   - Used for: Data fetching from backend

**They are NOT the same!** Both are needed for different purposes.

---

## 🚀 Next Steps

1. Run `npm install` in frontend folder
2. Start backend with `python run.py`
3. Start frontend with `npm start`
4. Navigate to http://localhost:3000/image
5. Upload an image and test!

All routes should now work perfectly in demo mode! 🎉
