from __future__ import annotations

import os
from typing import Optional, Tuple

import numpy as np
import supervision as sv
import torch
from ultralytics import YOLO

_PERSON_CLASS_ID = 0
_BALL_CLASS_ID = 32
_CONFIDENCE_THRESHOLD = 0.4


def _select_device() -> str:
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"
    return "cpu"


class PlayerDetector:
    _instance: Optional["PlayerDetector"] = None
    _model: Optional[YOLO] = None

    def __new__(cls, models_dir: str = "models") -> "PlayerDetector":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, models_dir: str = "models") -> None:
        if self._initialized:
            return
        self._device = _select_device()
        model_path = os.path.join(models_dir, "yolov8n.pt")
        self._model = YOLO(model_path)
        self._model.to(self._device)
        self._initialized = True

    def detect(
        self, frame: np.ndarray
    ) -> Tuple[sv.Detections, sv.Detections]:
        results = self._model(
            frame,
            conf=_CONFIDENCE_THRESHOLD,
            device=self._device,
            verbose=False,
        )[0]

        detections = sv.Detections.from_ultralytics(results)

        if len(detections) == 0:
            empty = sv.Detections.empty()
            return empty, empty

        person_mask = detections.class_id == _PERSON_CLASS_ID
        ball_mask = detections.class_id == _BALL_CLASS_ID

        player_detections = detections[person_mask]
        ball_detections = detections[ball_mask]

        return player_detections, ball_detections


def get_detector(models_dir: str = "models") -> PlayerDetector:
    return PlayerDetector(models_dir=models_dir)
