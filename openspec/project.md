# Project Context

## Purpose
Crowd Flow Prediction Analyzer is a comprehensive solution for real-time crowd monitoring and analysis. The system provides:
- Real-time crowd counting using computer vision models
- Multi-camera support for monitoring different locations
- Historical data analysis and visualization
- Web-based dashboard for monitoring and management
- HLS streaming for efficient video delivery

## Tech Stack
### Backend
- Python 3.9+
- FastAPI for RESTful API
- OpenCV for computer vision processing
- Pydantic for data validation
- SQLAlchemy for database operations (if applicable)
- Uvicorn as ASGI server

### Frontend
- React 19
- React Router for navigation
- HLS.js for video streaming
- Chart.js for data visualization
- React Testing Library for testing

### Machine Learning
- PyTorch for deep learning models
- Custom implementations of CSRNet and VMamba models
- OpenCV for image processing
- NumPy for numerical operations

### Infrastructure
- HLS (HTTP Live Streaming) for video delivery
- WebSockets for real-time updates
- Prometheus for monitoring

## Project Conventions

### Code Style
- Python: PEP 8 compliant with 4-space indentation
- JavaScript/React: Standard JavaScript with React Hooks
- Docstrings: Google style for Python, JSDoc for JavaScript
- File naming: kebab-case for all files
- Component naming: PascalCase for React components

### Architecture Patterns
- Backend: RESTful API with FastAPI
- Frontend: Component-based architecture with React
- State Management: React Context API for global state
- Real-time: WebSockets for live updates
- Video: HLS for adaptive bitrate streaming

### Testing Strategy
- Unit tests for core functionality
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Test coverage target: 80%+
- Backend: pytest
- Frontend: React Testing Library

### Git Workflow
- Branching: Git Flow
- Commit messages: Conventional Commits
- PRs required for all changes
- Main branch protected
- Commit message format:
  ```
  type(scope): description
  
  [optional body]
  
  [optional footer(s)]
  ```
  Types: feat, fix, docs, style, refactor, test, chore

## Domain Context
- Computer Vision: Object detection and crowd counting
- Video Processing: Real-time video analysis
- Web Development: Dashboard and monitoring
- Machine Learning: Model inference and optimization

## Important Constraints
- Real-time processing requirements
- Scalability for multiple camera streams
- Resource efficiency for edge deployment
- Data privacy and security compliance
- Browser compatibility (modern browsers only)

## External Dependencies
### Backend
- FastAPI
- OpenCV
- PyTorch
- Pydantic
- SQLAlchemy (if using database)
- Uvicorn

### Frontend
- React 19
- React Router
- HLS.js
- Chart.js
- Axios for API calls

### Development
- pytest
- Black (code formatter)
- ESLint
- Prettier

## Getting Started
1. Install backend dependencies: `pip install -r requirements.txt`
2. Install frontend dependencies: `cd frontend && npm install`
3. Start backend: `uvicorn app.main:app --reload`
4. Start frontend: `cd frontend && npm start`

## Project Structure
```
├── backend/            # Backend FastAPI application
│   ├── app/            # Main application package
│   ├── models/         # ML models and inference
│   └── tests/          # Backend tests
├── frontend/           # React frontend application
│   ├── public/         # Static assets
│   └── src/            # React components and logic
├── ml/                 # Machine learning models and training
└── scripts/            # Utility scripts
```
