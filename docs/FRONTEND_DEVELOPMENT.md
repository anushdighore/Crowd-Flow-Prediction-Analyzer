# Frontend Development Guide

This document provides all necessary information for developing a new frontend for the Multi-Model Crowd Counting System.

## Original Implementation

- **Frontend URL**: `http://localhost:3000` (default React development server)
- **Production URL**: Update with your production URL when deployed

## Table of Contents
1. [System Requirements](#system-requirements)
2. [API Documentation](#api-documentation)
3. [Environment Setup](#environment-setup)
4. [Project Structure](#project-structure)
5. [Key Features Implementation](#key-features-implementation)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Deployment](#deployment)

## System Requirements

- Node.js 16.14.0 or later
- npm 8.3.1 or later
- Backend server running (see [Backend Documentation](../backend/README.md))
- Modern web browser (Chrome, Firefox, Edge, or Safari latest versions)

## API Documentation

### Base URLs
- **API Base URL**: `http://localhost:8000/api/v1`
- **Development**: `http://localhost:8000`
- **Production**: `https://your-production-url.com` (Update in production)

### Available Models

1. **CSRNet**
   - ID: `CSRNet`
   - Type: Density-based crowd counting
   - Endpoint: `/predict/csrnet`

2. **VMamba TMTB**
   - ID: `VMamba`
   - Type: Vision Mamba architecture
   - Endpoint: `/predict/vmamba`

3. **MCNN** (Coming Soon)
   - ID: `MCNN`
   - Type: Multi-column CNN

4. **YOLOv8** (Coming Soon)
   - ID: `YOLOv8`
   - Type: Object detection

### Authentication
Currently, the API doesn't require authentication. All endpoints are open.

### Endpoints

#### 1. Health Check
- **Endpoint**: `GET /health`
- **Response**:
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

#### 2. Image Prediction
- **Endpoint**: `POST /predict/{model_id}`
- **Available Models**: `csrnet`, `vmamba`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Image file (required)
  - `return_density`: Boolean to include density map (default: `true`)
- **Example Request**:
  ```bash
  curl -X POST \
    'http://localhost:8000/api/v1/predict/csrnet' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'file=@image.jpg' \
    -F 'return_density=true'
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "count": 42,
      "density_map": "base64_encoded_image",
      "processing_time": 0.45
    }
  }
  ```

#### 3. Real-time WebSocket
- **Endpoint**: `ws://localhost:8000/ws`
- **Events**:
  - `connect`: Connection established
  - `prediction`: New prediction data
  - `error`: Error occurred
  - `disconnect`: Connection closed

#### 4. Camera Management
- **List Cameras**: `GET /cameras`
- **Add Camera**: `POST /cameras`
  ```json
  {
    "name": "Entrance Camera",
    "stream_url": "rtsp://camera-feed",
    "location": {"x": 0, "y": 0}
  }
  ```
- **Get Camera Status**: `GET /cameras/{camera_id}/status`
- **Update Camera**: `PUT /cameras/{camera_id}`
- **Delete Camera**: `DELETE /cameras/{camera_id}`

#### 5. Historical Data
- **Get Predictions**: `GET /predictions`
  - Query Params: 
    - `start_date`: ISO date string
    - `end_date`: ISO date string
    - `camera_id`: Filter by camera
    - `model`: Filter by model
- **Get Prediction**: `GET /predictions/{prediction_id}`

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_WS_URL=ws://localhost:8000
   NODE_ENV=development
   ```

4. **Start development server**
   ```bash
   npm start
   # or
   yarn start
   ```

## Project Structure

### Directory Overview

```
frontend/
├── public/                # Static files
└── src/
    ├── components/        # Reusable UI components
    │   ├── CameraSelector.js    # Camera selection dropdown
    │   ├── CameraStream.js      # Camera feed display
    │   ├── ExternalCam.js       # External camera integration
    │   ├── HLSPlayer.js         # HLS video player
    │   ├── SimpleChart.js       # Data visualization
    │   └── WebcamCounter.css    # Webcam component styles
    │
    ├── models/             # Model-specific components
    │   ├── App_multimodel.js   # Main model interface
    │   ├── CSRNetUploader.js   # CSRNet implementation
    │   ├── MCNNUploader.js     # MCNN implementation
    │   ├── VMambaUploader.js   # VMamba implementation
    │   └── YOLOUploader.js     # YOLO implementation
    │
    ├── pages/              # Page components
    │   ├── CameraPage.js        # Camera feed page
    │   └── HLSStreamingPage.js  # HLS streaming page
    │
    ├── App.js             # Main application component
    ├── App.css            # Global styles
    └── index.js           # Application entry point
```

## Component Documentation

### 1. Core Components

#### CameraSelector
- **Purpose**: Dropdown to select different camera sources
- **Props**:
  - `cameras`: Array of available cameras
  - `onSelect`: Callback when camera is selected
  - `selectedCamera`: Currently selected camera
- **Usage**:
  ```jsx
  <CameraSelector 
    cameras={availableCameras}
    selectedCamera={currentCamera}
    onSelect={handleCameraSelect}
  />
  ```

#### CameraStream
- **Purpose**: Displays video stream from a camera
- **Props**:
  - `stream`: MediaStream object
  - `className`: Additional CSS classes
- **Features**:
  - Auto-plays video
  - Handles stream cleanup

#### ExternalCam
- **Purpose**: Manages external camera connections
- **Props**:
  - `url`: RTSP/HTTP stream URL
  - `onError`: Error handler
  - `autoPlay`: Auto-play stream
- **Features**:
  - RTSP to WebRTC conversion
  - Error handling
  - Auto-reconnection

### 2. Model Components

#### App_multimodel
- **Main model interface**
- **State Management**:
  - Selected model
  - Processing status
  - Prediction results
- **Methods**:
  - `handleModelChange()`
  - `processPrediction()`
  - `handleError()`

#### Model Uploaders (CSRNet, VMamba, MCNN, YOLO)
- **Common Props**:
  - `onPrediction`: Callback with prediction results
  - `disabled`: Disable controls
  - `loading`: Show loading state
- **Methods**:
  - `handleFileUpload()`
  - `processImage()`
  - `resetState()`

### 3. Page Components

#### CameraPage
- **Purpose**: Main camera interface
- **Features**:
  - Camera feed display
  - Model selection
  - Real-time predictions
  - Controls for capture/analysis

#### HLSStreamingPage
- **Purpose**: HLS video streaming
- **Features**:
  - HLS.js integration
  - Adaptive bitrate
  - Stream health monitoring

## Web-Based Development Setup

### 1. CodeSandbox Setup

1. Go to [CodeSandbox](https://codesandbox.io/)
2. Create new React project
3. Install dependencies:
   ```bash
   npm install axios hls.js react-webcam @chakra-ui/react @emotion/react @emotion/styled framer-motion
   ```

### 2. Key Dependencies

```json
{
  "dependencies": {
    "@chakra-ui/react": "^2.8.0",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.2",
    "hls.js": "^1.4.12",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "react-webcam": "^7.2.4",
    "recharts": "^2.10.4"
  }
}
```

### 3. Component Implementation Example

```jsx
// Example: CameraFeed.jsx
import React, { useRef, useEffect } from 'react';
import { Box, Text } from '@chakra-ui/react';
import Webcam from 'react-webcam';

const CameraFeed = ({ onFrame, width = 640, height = 480 }) => {
  const webcamRef = useRef(null);
  
  const capture = React.useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    onFrame && onFrame(imageSrc);
  }, [webcamRef, onFrame]);

  useEffect(() => {
    const interval = setInterval(capture, 1000); // Capture every second
    return () => clearInterval(interval);
  }, [capture]);

  return (
    <Box position="relative" width={`${width}px`}>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={width}
        height={height}
      />
      <Text mt={2} textAlign="center">Live Camera Feed</Text>
    </Box>
  );
};

export default CameraFeed;
```

### 4. Integration with Backend

```javascript
// api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const predictImage = async (imageData, model = 'csrnet') => {
  const formData = new FormData();
  formData.append('file', imageData);
  
  try {
    const response = await axios.post(
      `${API_URL}/predict/${model}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Prediction error:', error);
    throw error;
  }
};
```

### 5. Styling with Chakra UI

```jsx
// Theme configuration
import { ChakraProvider, extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      500: '#3182ce',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'bold',
        borderRadius: 'md',
      },
    },
  },
});

// Usage in App.js
function App() {
  return (
    <ChakraProvider theme={theme}>
      {/* Your app components */}
    </ChakraProvider>
  );
}
```

## Development Workflow

1. **Component Development**
   - Create components in `src/components`
   - Use Storybook for isolated development
   - Write unit tests with Jest and React Testing Library

2. **State Management**
   - Use React Context for global state
   - Consider Redux for complex state
   - Use React Query for server state

3. **Styling**
   - Use Chakra UI components
   - Custom styles with `sx` prop
   - Responsive design with array syntax

4. **Testing**
   - Unit tests: `npm test`
   - E2E tests: Cypress
   - Visual regression: Storybook + Chromatic
├── public/               # Static files
├── src/
│   ├── api/              # API service layer
│   ├── assets/           # Images, fonts, etc.
│   ├── components/       # Reusable UI components
│   ├── contexts/         # React contexts
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   ├── services/         # Business logic services
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main App component
│   └── index.tsx         # Application entry point
├── .env                 # Environment variables
├── package.json         # Dependencies and scripts
└── tsconfig.json        # TypeScript configuration
```

## Key Features Implementation

### 1. Real-time Video Processing
```typescript
// Example using WebSocket for real-time updates
import { useEffect, useRef } from 'react';

const useWebSocket = (url: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => {
      ws.current?.close();
    };
  }, [url, onMessage]);

  return ws.current;
};
```

### 2. Image Upload and Prediction
```typescript
// Example API service
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const predictImage = async (file: File, model: string = 'csrnet') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_URL}/predict?model=${model}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
```

### 3. Error Handling
```typescript
// Error handling utility
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// API client with error handling
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      throw new ApiError(
        error.response.status,
        error.response.data?.error?.code || 'UNKNOWN_ERROR',
        error.response.data?.error?.message || 'An unknown error occurred'
      );
    }
    throw error;
  }
);
```

## Development Workflow

1. **Branching Strategy**
   - `main` - Production-ready code
   - `develop` - Integration branch for features
   - `feature/*` - New features
   - `bugfix/*` - Bug fixes
   - `hotfix/*` - Critical production fixes

2. **Coding Standards**
   - Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
   - Use TypeScript for all new code
   - Write unit tests for new features
   - Document complex logic with JSDoc

3. **Code Quality**
   ```bash
   # Run linter
   npm run lint
   
   # Run type checking
   npm run type-check
   
   # Run tests
   npm test
   ```

## Testing

### Unit Tests
```typescript
// Example test with React Testing Library
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PredictButton } from './PredictButton';

describe('PredictButton', () => {
  it('calls onClick handler when clicked', async () => {
    const handleClick = jest.fn();
    render(<PredictButton onClick={handleClick} />);
    
    await userEvent.click(screen.getByRole('button', { name: /predict/i }));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Tests
```typescript
// Example API integration test
describe('API Service', () => {
  it('successfully calls the predict endpoint', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    
    const response = await predictImage(mockFile);
    
    expect(response).toHaveProperty('success', true);
    expect(response.data).toHaveProperty('count');
    expect(response.data).toHaveProperty('density_map');
  });
});
```

## Deployment

### Build for Production
```bash
npm run build
```

### Environment Variables for Production
```env
REACT_APP_API_URL=https://your-production-api.com
REACT_APP_WS_URL=wss://your-production-api.com
NODE_ENV=production
```

### Deployment Options

1. **Static Hosting**
   - Netlify
   - Vercel
   - GitHub Pages
   - AWS S3 + CloudFront

2. **Docker**
   ```dockerfile
   # Dockerfile
   FROM node:16-alpine as build
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=build /app/build /usr/share/nginx/html
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure the backend has proper CORS headers
   - Verify the API URL is correct in your environment variables

2. **WebSocket Connection Issues**
   - Check if the WebSocket server is running
   - Verify the WebSocket URL protocol (ws:// for HTTP, wss:// for HTTPS)

3. **Build Failures**
   - Clear node_modules and reinstall dependencies
   - Check for TypeScript errors
   - Ensure all environment variables are set

## Support

For additional help, please contact the development team or open an issue in the repository.
