# Routing Structure Setup

## Overview

Your application now has a complete routing structure with three main pages:

### 1. **Landing Page** (`/`)

- **Path**: `src/pages/LandingPage.js`
- **Purpose**: Public landing page with features showcase
- **Features**:
  - Navigation bar with Sign In button
  - Hero section with call-to-action
  - Features showcase (6 feature cards)
  - AI models overview
  - Call-to-action section
  - Responsive design

### 2. **Dashboard** (`/dashboard`)

- **Path**: `src/pages/Dashboard.js`
- **Purpose**: Main application with all crowd counting features
- **Features**:
  - Protected route (requires authentication)
  - Navigation menu with 6 modes
  - Model selection interface
  - All model uploaders (CSRNet, VMamba, YOLO, MCNN)
  - Webcam support
  - External camera streaming
  - HLS streaming
  - Pedestrian tracking
  - Logout functionality

### 3. **Login Page** (`/login`)

- **Path**: `src/pages/LoginPage.js`
- **Purpose**: Authentication page
- **Status**: Already exists in your project

## Router Configuration

**File**: `src/router/index.js`

Routes defined:

```
/                  → LandingPage (public)
/login             → LoginPage (public)
/dashboard         → Dashboard (protected - requires auth)
*                  → LandingPage (fallback)
```

## Authentication Flow

1. **Unauthenticated Users**:

   - Visit `/` → See Landing Page
   - Try to visit `/dashboard` → Redirected to Login
   - Click "Sign In" on landing → Go to Login

2. **Authenticated Users**:
   - Visit `/` → See Landing Page with "Dashboard" button
   - Visit `/dashboard` → Access full dashboard
   - Can logout from dashboard

## File Structure

```
frontend/src/
├── router/
│   └── index.js                      (Main router configuration)
├── pages/
│   ├── LandingPage.js               (New - Public landing page)
│   ├── LandingPage.css              (New - Landing page styles)
│   ├── Dashboard.js                 (New - Main dashboard)
│   ├── Dashboard.css                (New - Dashboard styles)
│   ├── LoginPage.js                 (Existing - Auth page)
│   └── ...
├── components/
│   ├── Nav/                         (Navigation bar)
│   ├── Models/                      (Model uploaders)
│   ├── Camera/                      (Camera components)
│   └── ...
├── index.js                         (Updated - Uses AppRouter)
└── App.js                           (Original - Can be kept or removed)
```

## Styling

### LandingPage.css

- Gradient background (purple theme)
- Sticky navigation bar
- Hero section with animations
- Responsive grid layouts
- Feature and model cards
- Call-to-action sections

### Dashboard.css

- White header with logout button
- Model selection interface
- Responsive grid for model options
- Uploader section styling
- Authentication check screen

## Navigation

The `Nav` component is included in the Dashboard and handles:

- Mode switching (Upload, Video, Webcam, External, HLS, Pedestrian)
- User profile display
- Responsive design (icons on mobile, labels on desktop)

## Getting Started

1. **Start the application**:

   ```bash
   npm start
   ```

2. **Access the pages**:

   - Landing Page: `http://localhost:3000/`
   - Dashboard: `http://localhost:3000/dashboard`
   - Login: `http://localhost:3000/login`

3. **Authentication**:
   - Log in through the login page
   - Access dashboard with full features
   - Log out from the dashboard header

## Notes

- All routes are protected based on authentication status
- Users are automatically redirected to login if they try to access dashboard without authentication
- The landing page is accessible to both authenticated and unauthenticated users
- Responsive design works on mobile, tablet, and desktop screens
