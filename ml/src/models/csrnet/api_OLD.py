"""High-level CSRNet inference helpers wired into the new core managers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, cast

import cv2  # type: ignore[import]
import numpy as np
from PIL import Image

from ...core.device_manager import DeviceManager, get_device_manager
from ...core.inference_engine import InferenceEngine, get_inference_engine
from ...core.model_manager import ModelManager, get_model_manager
from ...preprocessing.csrnet_preprocess import CSRNetPreprocessor

# Legacy FastAPI module keeps the original transforms/checks.
# We import it to reuse constants like `transform` if needed.
from . import api_old_fastapi as legacy_api

cv2 = cast(Any, cv2)

logger = logging.getLogger(__name__)


class CSRNetAPI:
    """Thin wrapper around the inference engine for CSRNet."""

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        device_manager: Optional[DeviceManager] = None,
        inference_engine: Optional[InferenceEngine] = None,
        preprocessor: Optional[CSRNetPreprocessor] = None,
        auto_load: bool = True,
        warmup: bool = True,
    ) -> None:
        self.model_name = "csrnet"
        self.device_manager = device_manager or get_device_manager()
        self.model_manager = model_manager or get_model_manager(device_manager=self.device_manager)
        self.inference_engine = inference_engine or get_inference_engine(
            model_manager=self.model_manager,
            device_manager=self.device_manager,
        )
        self.preprocessor = preprocessor or CSRNetPreprocessor()

        # Preserve the exact preprocessing pipeline from the legacy API if available.
        legacy_transform = getattr(legacy_api, "transform", None)
        if legacy_transform is not None:
            self.preprocessor.transform = legacy_transform  # type: ignore[assignment]

        if auto_load:
            self.load_model(warmup=warmup)

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------
    def load_model(self, *, device: Optional[str] = None, warmup: bool = True) -> None:
        """Load CSRNet via the shared model manager."""

        target_device = device or self.device_manager.get_best_device()
        logger.info("Loading CSRNet on %s", target_device)

        self.model_manager.load_model(self.model_name, device=target_device)

        if warmup:
            self.model_manager.warmup_model(self.model_name)

    def unload_model(self) -> None:
        """Unload CSRNet and release memory."""

        self.model_manager.unload_model(self.model_name)

    def switch_device(self, device: str) -> None:
        """Move CSRNet to a new device using ModelManager."""

        self.model_manager.switch_device(self.model_name, device)

    # ------------------------------------------------------------------
    # Public inference helpers
    # ------------------------------------------------------------------
    def predict_image(
        self,
        image: Union[str, Path, Any, Image.Image],
        *,
        return_density_map: bool = False,
    ) -> Dict[str, Any]:
        """Predict crowd count for a single image."""

        image_np = self._ensure_numpy(image)
        return self.inference_engine.infer_single(  # type: ignore[call-arg]
            image_np,
            self.model_name,
            return_density_map=return_density_map,
        )

    def predict_batch(
        self,
        images: Iterable[Union[str, Path, Any, Image.Image]],
        *,
        return_density_maps: bool = False,
    ) -> List[Dict[str, Any]]:
        """Predict on a batch of images."""

        image_arrays = [self._ensure_numpy(img) for img in images]
        return self.inference_engine.infer_batch(  # type: ignore[call-arg]
            image_arrays,
            self.model_name,
            return_density_maps=return_density_maps,
        )

    def predict_video(
        self,
        video_path: Union[str, Path],
        *,
        callback: Optional[Callable[[int, Any, Dict[str, Any]], None]] = None,
        max_fps: Optional[int] = None,
        skip_frames: int = 0,
    ) -> List[Dict[str, Any]]:
        """Iterate through a video file and run CSRNet."""
        cap = cast(Any, cv2.VideoCapture(str(video_path)))  # type: ignore[attr-defined]
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        results: List[Dict[str, Any]] = []
        frame_idx = 0

        def frame_generator() -> Iterable[Any]:
            nonlocal frame_idx
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if skip_frames > 0 and frame_idx % (skip_frames + 1) != 0:
                    frame_idx += 1
                    continue

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # type: ignore
                frame_idx += 1
                yield frame_rgb

        def frame_callback(frame: Any, result: Dict[str, Any]) -> None:
            result_with_idx: Dict[str, Any] = {**result, "frame_idx": frame_idx - 1}
            results.append(result_with_idx)
            if callback:
                callback(frame_idx - 1, frame, result_with_idx)

        try:
            self.inference_engine.infer_stream(  # type: ignore[call-arg]
                frame_generator(),
                self.model_name,
                callback=frame_callback,
                max_fps=max_fps,
            )
        finally:
            cap.release()

        return results

    def predict_webcam(
        self,
        *,
        camera_index: int = 0,
        callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
        max_fps: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Run CSRNet on a local webcam feed."""

        self._predict_camera_stream(
            camera_index,
            callback=callback,
            max_fps=max_fps,
            duration=duration,
        )

    def predict_camera(
        self,
        camera_url: str,
        *,
        callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
        max_fps: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Run CSRNet on an external camera (RTSP/HTTP)."""

        self._predict_camera_stream(
            camera_url,
            callback=callback,
            max_fps=max_fps,
            duration=duration,
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Return metadata for CSRNet and aggregated inference stats."""

        return {
            "model": self.model_manager.get_model_info(self.model_name),
            "inference": self.inference_engine.get_stats(),
        }

    def reset_stats(self) -> None:
        """Reset inference statistics."""

        self.inference_engine.reset_stats()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _predict_camera_stream(
        self,
        source: Union[int, str],
        *,
        callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
        max_fps: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        cap = cast(Any, cv2.VideoCapture(source))  # type: ignore[attr-defined]
        if not cap.isOpened():
            raise ValueError(f"Cannot open camera source: {source}")

        logger.info("Starting CSRNet stream on %s", source)

        from time import time

        start_time = time()

        def frame_generator() -> Iterable[Any]:
            while cap.isOpened():
                if duration and (time() - start_time) > duration:
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # type: ignore

        try:
            self.inference_engine.infer_stream(  # type: ignore
                frame_generator(),
                self.model_name,
                callback=callback,
                max_fps=max_fps,
            )
        finally:
            cap.release()
            logger.info("Stream finished for %s", source)

    def _ensure_numpy(self, image: Union[str, Path, Any, Image.Image]) -> Any:
        if isinstance(image, np.ndarray):
            return self._ensure_rgb(image)
        if isinstance(image, (str, Path)):
            pil_image = Image.open(Path(image)).convert("RGB")
            return np.array(pil_image)
        if isinstance(image, Image.Image):
            return np.array(image.convert("RGB"))
        raise TypeError(f"Unsupported image type: {type(image)!r}")

    @staticmethod
    def _ensure_rgb(array: Any) -> Any:
        if array.ndim == 2:
            return cv2.cvtColor(array, cv2.COLOR_GRAY2RGB)  # type: ignore
        if array.shape[-1] == 4:
            return cv2.cvtColor(array, cv2.COLOR_RGBA2RGB)  # type: ignore
        return array


# Convenience helpers ---------------------------------------------------------

_shared_api: Optional[CSRNetAPI] = None


def get_csrnet_api() -> CSRNetAPI:
    global _shared_api
    if _shared_api is None:
        _shared_api = CSRNetAPI()
    return _shared_api


def predict_image(
    image: Union[str, Path, Any, Image.Image],
    *,
    return_density_map: bool = False,
) -> Dict[str, Any]:
    api = get_csrnet_api()
    return api.predict_image(image, return_density_map=return_density_map)


def predict_batch(
    images: Iterable[Union[str, Path, Any, Image.Image]],
    *,
    return_density_maps: bool = False,
) -> List[Dict[str, Any]]:
    api = get_csrnet_api()
    return api.predict_batch(images, return_density_maps=return_density_maps)


def predict_video(
    video_path: Union[str, Path],
    *,
    callback: Optional[Callable[[int, Any, Dict[str, Any]], None]] = None,
    max_fps: Optional[int] = None,
    skip_frames: int = 0,
) -> List[Dict[str, Any]]:
    api = get_csrnet_api()
    return api.predict_video(
        video_path,
        callback=callback,
        max_fps=max_fps,
        skip_frames=skip_frames,
    )


def predict_webcam(
    *,
    camera_index: int = 0,
    callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
    max_fps: Optional[int] = None,
    duration: Optional[float] = None,
) -> None:
    api = get_csrnet_api()
    api.predict_webcam(
        camera_index=camera_index,
        callback=callback,
        max_fps=max_fps,
        duration=duration,
    )


def predict_camera(
    camera_url: str,
    *,
    callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
    max_fps: Optional[int] = None,
    duration: Optional[float] = None,
) -> None:
    api = get_csrnet_api()
    api.predict_camera(
        camera_url,
        callback=callback,
        max_fps=max_fps,
        duration=duration,
    )
