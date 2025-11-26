# Input Modes Report

- Upload Image
  - Endpoint: `POST /api/v1/yolo/detect` (`frontend/src/components/Models/YOLO/YOLOUploader.js:112`).
  - Models: YOLOv8; CSRNet via `/api/v1/csrnet/count` (`frontend/src/components/Models/CSRNet/CSRNetUploader.js:92`).
  - Outputs: boxes, annotated image; count, heatmap.
  - Status: Working.

- Upload Video
  - Endpoint: `WS /ws/video-process` (`frontend/src/components/Models/YOLO/VideoUploader.js:90`).
  - Models: YOLO tracking with `UnifiedCounter`.
  - Outputs: annotated frames, tracks, metrics.
  - Status: Partially working; ensure backend running and payload format matches.

- Live Webcam
  - Endpoint: `WS /ws/count` (`frontend/src/context/WebcamContext.js:72`).
  - Models: CSRNet, TMTB, YOLOv8 (via mapped `yolo-*`).
  - Outputs: count, fps, inference_time_ms, heatmap, boxes/tracks.
  - Status: Working after patches.

- External IP Camera
  - Endpoint: `WS /ws/external-camera` (`frontend/src/pages/ExternalCamera/ExternalCamera.js:15`).
  - Models: CSRNet/TMTB/YOLO; WS “get_frame” polling.
  - Outputs: frame JPEG, heatmap, metrics.
  - Status: Working.

