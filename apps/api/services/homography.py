from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


def compute_homography(
    image_points: List[dict],
    frame_width: int,
    frame_height: int,
    field_width_m: float,
    field_height_m: float,
) -> dict:
    if len(image_points) != 4:
        return {"matrix": None, "reprojection_error": float("inf"), "valid": False}

    src_pts = np.array(
        [[pt["x"], pt["y"]] for pt in image_points], dtype=np.float32
    )

    dst_pts = np.array(
        [
            [0.0, 0.0],
            [field_width_m, 0.0],
            [field_width_m, field_height_m],
            [0.0, field_height_m],
        ],
        dtype=np.float32,
    )

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if H is None:
        return {"matrix": None, "reprojection_error": float("inf"), "valid": False}

    error = validate_homography(H, src_pts, dst_pts)
    valid = error < 5.0

    return {
        "matrix": H.tolist(),
        "reprojection_error": float(error),
        "valid": valid,
    }


def pixel_to_meters(
    H: np.ndarray, pixel_point: Tuple[float, float]
) -> Tuple[float, float]:
    src = np.array([[[pixel_point[0], pixel_point[1]]]], dtype=np.float32)
    dst = cv2.perspectiveTransform(src, H)
    x_m = float(dst[0][0][0])
    y_m = float(dst[0][0][1])
    return x_m, y_m


def validate_homography(
    H: np.ndarray, src_pts: np.ndarray, dst_pts: np.ndarray
) -> float:
    src_reshaped = src_pts.reshape(-1, 1, 2).astype(np.float32)
    projected = cv2.perspectiveTransform(src_reshaped, H)
    projected = projected.reshape(-1, 2)

    errors = np.linalg.norm(projected - dst_pts, axis=1)
    return float(np.mean(errors))
