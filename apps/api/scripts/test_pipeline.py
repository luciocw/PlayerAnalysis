"""
Smoke test for Fase 0 pipeline validation.

Usage:
    python scripts/test_pipeline.py --video path/to/test.mp4
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

import cv2
import numpy as np

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_API_DIR = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _API_DIR)

from services.detector import get_detector
from services.frame_extractor import extract_first_frame, get_video_info
from services.homography import compute_homography, pixel_to_meters
from services.metrics import MetricsAccumulator
from services.tracker import PlayerTracker


_MOCK_IMAGE_POINTS = [
    {"x": 100.0, "y": 80.0},
    {"x": 1180.0, "y": 80.0},
    {"x": 1180.0, "y": 640.0},
    {"x": 100.0, "y": 640.0},
]

_FIELD_WIDTH_M = 40.0
_FIELD_HEIGHT_M = 20.0
_MODELS_DIR = os.path.join(_API_DIR, "models")


def _step_extract_first_frame(video_path: str, tmp_dir: str) -> str:
    print("[1/6] Extracting first frame...")
    frame_path = os.path.join(tmp_dir, "first_frame.jpg")
    extract_first_frame(video_path, frame_path)
    info = get_video_info(video_path)
    print(
        f"      Video: {info['width']}x{info['height']} @ {info['fps']:.2f} fps, "
        f"{info['total_frames']} frames ({info['duration_seconds']:.1f}s)"
    )
    print(f"      First frame saved to: {frame_path}")
    return frame_path


def _step_detect_first_frame(frame_path: str) -> None:
    print("[2/6] Running detector on first frame...")
    detector = get_detector(models_dir=_MODELS_DIR)
    frame = cv2.imread(frame_path)
    if frame is None:
        raise RuntimeError(f"Cannot read frame from {frame_path}")
    players, balls = detector.detect(frame)
    print(f"      Detected players: {len(players)}")
    print(f"      Detected balls:   {len(balls)}")


def _step_track_first_n_frames(video_path: str, n_frames: int = 90) -> set[int]:
    print(f"[3/6] Tracking first {n_frames} frames...")
    detector = get_detector(models_dir=_MODELS_DIR)
    tracker = PlayerTracker()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    unique_ids: set[int] = set()
    frame_idx = 0
    while frame_idx < n_frames:
        ret, frame = cap.read()
        if not ret:
            break
        players, _ = detector.detect(frame)
        tracked = tracker.update(players)
        if tracked.tracker_id is not None:
            unique_ids.update(int(tid) for tid in tracked.tracker_id)
        frame_idx += 1

    cap.release()
    print(f"      Unique track IDs seen: {sorted(unique_ids)}")
    return unique_ids


def _step_compute_homography(frame_path: str) -> np.ndarray:
    print("[4/6] Computing homography...")
    frame = cv2.imread(frame_path)
    if frame is None:
        raise RuntimeError(f"Cannot read frame from {frame_path}")
    h, w = frame.shape[:2]
    result = compute_homography(
        _MOCK_IMAGE_POINTS, w, h, _FIELD_WIDTH_M, _FIELD_HEIGHT_M
    )
    print(f"      Reprojection error: {result['reprojection_error']:.4f} px")
    print(f"      Homography valid: {result['valid']}")
    if result["matrix"] is None:
        raise RuntimeError("Homography computation returned None matrix.")
    H = np.array(result["matrix"], dtype=np.float64)
    test_pt = pixel_to_meters(H, (640.0, 360.0))
    print(f"      Pixel (640, 360) → meters {test_pt}")
    return H


def _step_run_metrics(video_path: str, H: np.ndarray, n_frames: int = 90) -> dict:
    print(f"[5/6] Running metrics accumulation for first {n_frames} frames...")
    info = get_video_info(video_path)
    fps = info["fps"]
    sample_rate = 6
    accumulator = MetricsAccumulator(
        fps=fps,
        H=H,
        sample_rate=sample_rate,
        sprint_speed_kmh=18.0,
        sprint_min_frames=15,
    )
    detector = get_detector(models_dir=_MODELS_DIR)
    tracker = PlayerTracker()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    frame_number = 0
    while frame_number < n_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_number % sample_rate == 0:
            players, _ = detector.detect(frame)
            tracked = tracker.update(players)
            accumulator.update(tracked, frame_number)
        frame_number += 1

    cap.release()
    metrics = accumulator.finalize()
    df = accumulator.get_summary_dataframe()
    print(f"      Players tracked: {len(metrics['players'])}")
    if not df.empty:
        print(df.to_string(index=False))
    return metrics


def _step_print_summary(metrics: dict) -> None:
    print("[6/6] Metrics summary:")
    for player in metrics.get("players", []):
        print(
            f"      {player['label']} | "
            f"dist={player['total_distance_m']:.1f}m | "
            f"max_speed={player['max_speed_kmh']:.1f}km/h | "
            f"sprints={player['sprint_count']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test for Fase 0 pipeline.")
    parser.add_argument("--video", required=True, help="Path to test video file.")
    args = parser.parse_args()

    video_path = os.path.abspath(args.video)
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        frame_path = _step_extract_first_frame(video_path, tmp_dir)
        _step_detect_first_frame(frame_path)
        _step_track_first_n_frames(video_path)
        H = _step_compute_homography(frame_path)
        metrics = _step_run_metrics(video_path, H)
        _step_print_summary(metrics)

    print("\n✓ Fase 0 OK")


if __name__ == "__main__":
    main()
