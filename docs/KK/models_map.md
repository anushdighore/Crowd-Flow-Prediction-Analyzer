# Models Map

- CSRNet
  - Invocation: `csrnet_api.predict(image, source="webcam", return_density_map=...)` (`backend/app/main.py:272-275`).
  - Checkpoint: `config.models.csrnet.checkpoint` (`backend/config/config.yaml:59-61`).
  - Device: `config.inference.device` (`backend/config/config.yaml:78`).
  - Hooks: REST `/api/v1/csrnet/*`, WS `/ws/count`.
  - Artifacts: `count`, `density_map`, `inference_time_ms`, `heatmap` overlay (WS post-process).

- TMTB/VMamba
  - Invocation: `tmtb_api.predict(image, source="webcam")` (`backend/app/main.py:266-270`).
  - Checkpoint: `config.models.vmamba_tmtb.checkpoint` (`backend/config/config.yaml:55`).
  - Device: `config.inference.device`.
  - Hooks: REST `/api/v1/tmtb/*`, WS `/ws/count`.
  - Artifacts: `count`, `inference_time_ms`, optional `density_map`.

- YOLOv8
  - Invocation: `yolo_api.predict(image, checkpoint_path, return_boxes, visualize)` (`backend/app/main.py:257-264`).
  - Checkpoints: `yolov8[n|s|m|l|x].pt` mapped from `yolo-*` (`backend/app/main.py:204-211`).
  - Device: `config.inference.device`.
  - Hooks: REST `/api/v1/yolo/*`, WS `/ws/count`.
  - Artifacts: `boxes`, `annotated_image`, `count` (persons), `inference_time_ms`, `tracks` when UnifiedCounter.

