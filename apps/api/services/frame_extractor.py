from __future__ import annotations

import numpy as np
import cv2


def extract_first_frame(video_path: str, output_path: str) -> str:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Could not read first frame from video.")

    cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return output_path


def get_video_info(video_path: str) -> dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    duration_seconds = total_frames / fps if fps > 0 else 0.0

    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_seconds": round(duration_seconds, 3),
    }


def extract_crop(
    frame: np.ndarray, xyxy: np.ndarray, padding: int = 10
) -> np.ndarray:
    h, w = frame.shape[:2]
    x1 = int(xyxy[0]) - padding
    y1 = int(xyxy[1]) - padding
    x2 = int(xyxy[2]) + padding
    y2 = int(xyxy[3]) + padding

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    if x2 <= x1 or y2 <= y1:
        return np.zeros((1, 1, 3), dtype=np.uint8)

    return frame[y1:y2, x1:x2].copy()
