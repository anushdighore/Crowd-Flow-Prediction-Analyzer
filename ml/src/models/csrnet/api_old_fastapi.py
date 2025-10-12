"""Legacy FastAPI implementation for CSRNet.

This module is kept intact so newer components can reuse the original
preprocessing pipeline (`transform`) and the reference API behaviour.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING, cast

import torch
import torchvision.transforms as transforms  # type: ignore[import]
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from torch.nn import Module

    def load_csrnet(checkpoint_path: str, device: str = "cpu") -> Module:
        ...
else:
    from .csrnet import load_csrnet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


app = FastAPI(title="CSRNet Crowd Counting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model: torch.nn.Module | None = None
model_device: torch.device | None = None

transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


async def load_model_on_startup() -> None:
    """Load the CSRNet checkpoint when the FastAPI app starts."""

    global model, model_device

    model_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("CSRNet legacy API starting on %s", model_device)

    checkpoint_path = Path("./checkpoint/csrnet.pth")
    if not checkpoint_path.exists():
        logger.error("Missing CSRNet checkpoint: %s", checkpoint_path)
        raise RuntimeError("CSRNet checkpoint not found")

    model = load_csrnet(str(checkpoint_path), device=str(model_device))
    model.eval()
    logger.info("Legacy CSRNet model loaded successfully")


app.add_event_handler("startup", load_model_on_startup)  # type: ignore[arg-type]


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "status": "running",
        "message": "CSRNet Crowd Counting API",
        "model_loaded": model is not None,
        "device": str(model_device) if model_device else None,
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy" if model is not None else "unavailable",
        "model_loaded": model is not None,
        "device": str(model_device) if model_device else None,
        "device_type": "GPU" if torch.cuda.is_available() else "CPU",
    }


@app.post("/count")
async def count_people(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    if model is None or model_device is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Could not read image")
        raise HTTPException(status_code=400, detail="Could not read image") from exc

    tensor = cast(torch.Tensor, transform(pil_image))
    image_tensor = tensor.unsqueeze(0).to(model_device)

    with torch.no_grad():
        density_map = model(image_tensor)  # type: ignore[misc]
        count = int(round(density_map.sum().item()))

    return {
        "success": True,
        "count": count,
        "image_size": f"{pil_image.width}x{pil_image.height}",
        "filename": file.filename,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
