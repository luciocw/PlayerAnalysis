from __future__ import annotations

import json
import os
import pickle
import time
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import supervision as sv

from .detector import get_detector
from .frame_extractor import extract_crop
from .heatmap import generate_heatmap
from .metrics import MetricsAccumulator
from .tracker import PlayerTracker


def _write_progress(
    sessions_dir: str,
    session_id: str,
    percent: int,
    stage: str,
    frames_done: int = 0,
    frames_total: int = 0,
    eta_seconds: int = 0,
    message: Optional[str] = None,
) -> None:
    session_path = os.path.join(sessions_dir, session_id)
    os.makedirs(session_path, exist_ok=True)
    progress: dict = {
        "percent": percent,
        "stage": stage,
        "frames_done": frames_done,
        "frames_total": frames_total,
        "eta_seconds": eta_seconds,
    }
    if message is not None:
        progress["message"] = message
    with open(os.path.join(session_path, "progress.json"), "w") as f:
        json.dump(progress, f)


def _save_checkpoint(
    sessions_dir: str,
    session_id: str,
    tracks_data: dict,
) -> None:
    checkpoint_path = os.path.join(
        sessions_dir, session_id, "tracks_checkpoint.pkl"
    )
    with open(checkpoint_path, "wb") as f:
        pickle.dump(tracks_data, f)


def run_pipeline(
    session_id: str,
    video_path: str,
    H: np.ndarray,
    selected_track_id: int,
    sessions_dir: str,
    models_dir: str,
    sample_every_n_frames: int = 6,
    batch_size: int = 8,
    sprint_speed_kmh: float = 18.0,
    sprint_min_frames: int = 15,
) -> None:
    session_path = os.path.join(sessions_dir, session_id)
    thumbnails_dir = os.path.join(session_path, "thumbnails")
    os.makedirs(session_path, exist_ok=True)
    os.makedirs(thumbnails_dir, exist_ok=True)

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        _write_progress(
            sessions_dir, session_id, 0, "detection", 0, total_frames, 0
        )

        detector = get_detector(models_dir=models_dir)
        tracker = PlayerTracker()
        accumulator = MetricsAccumulator(
            fps=fps,
            H=H,
            sample_rate=sample_every_n_frames,
            sprint_speed_kmh=sprint_speed_kmh,
            sprint_min_frames=sprint_min_frames,
        )

        thumbnail_best: Dict[int, Tuple[float, np.ndarray]] = {}
        sampled_frame_count = 0
        start_time = time.time()
        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_number % sample_every_n_frames != 0:
                frame_number += 1
                continue

            player_detections, _ = detector.detect(frame)
            tracked = tracker.update(player_detections)
            accumulator.update(tracked, frame_number)

            if frame_number <= 300 * sample_every_n_frames:
                _collect_thumbnails(
                    frame, tracked, thumbnail_best, thumbnails_dir
                )

            sampled_frame_count += 1

            if sampled_frame_count % 100 == 0:
                elapsed = time.time() - start_time
                percent = min(
                    99, int((frame_number / max(total_frames, 1)) * 100)
                )
                frames_per_sec = sampled_frame_count / max(elapsed, 1e-6)
                remaining_sampled = (
                    (total_frames - frame_number) / sample_every_n_frames
                )
                eta = int(remaining_sampled / max(frames_per_sec, 1e-6))
                _write_progress(
                    sessions_dir,
                    session_id,
                    percent,
                    "detection",
                    frame_number,
                    total_frames,
                    eta,
                )

            if sampled_frame_count % 1000 == 0:
                checkpoint_data = {
                    "sampled_frame_count": sampled_frame_count,
                    "frame_number": frame_number,
                    "player_ids": list(accumulator._players.keys()),
                }
                _save_checkpoint(sessions_dir, session_id, checkpoint_data)

            frame_number += 1

        cap.release()

        metrics = accumulator.finalize()

        metrics_path = os.path.join(session_path, "metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        target_player = _find_player_data(metrics, selected_track_id)
        positions_m = (
            [(p["x"], p["y"]) for p in target_player["positions_m"]]
            if target_player
            else []
        )
        player_label = target_player["label"] if target_player else "Jogador"

        heatmap_path = os.path.join(session_path, "heatmap.png")
        field_w = 40.0
        field_h = 20.0
        generate_heatmap(
            positions_m=positions_m,
            output_path=heatmap_path,
            field_width_m=field_w,
            field_height_m=field_h,
            player_label=player_label,
        )

        _flush_thumbnails(thumbnail_best, thumbnails_dir)

        _write_progress(
            sessions_dir, session_id, 100, "done", total_frames, total_frames, 0
        )

    except Exception as exc:
        _write_progress(
            sessions_dir,
            session_id,
            -1,
            "error",
            message=str(exc),
        )
        raise


def _collect_thumbnails(
    frame: np.ndarray,
    tracked: sv.Detections,
    thumbnail_best: Dict[int, Tuple[float, np.ndarray]],
    thumbnails_dir: str,
) -> None:
    if tracked.tracker_id is None:
        return

    for i, track_id in enumerate(tracked.tracker_id):
        track_id = int(track_id)
        confidence = float(tracked.confidence[i]) if tracked.confidence is not None else 0.5
        xyxy = tracked.xyxy[i]

        if track_id not in thumbnail_best or confidence > thumbnail_best[track_id][0]:
            crop = extract_crop(frame, xyxy)
            thumbnail_best[track_id] = (confidence, crop)


def _flush_thumbnails(
    thumbnail_best: Dict[int, Tuple[float, np.ndarray]],
    thumbnails_dir: str,
) -> None:
    for track_id, (_, crop) in thumbnail_best.items():
        if crop is None or crop.size == 0:
            continue
        out_path = os.path.join(thumbnails_dir, f"{track_id}.jpg")
        cv2.imwrite(out_path, crop, [cv2.IMWRITE_JPEG_QUALITY, 85])


def _find_player_data(metrics: dict, selected_track_id: int) -> Optional[dict]:
    for player in metrics.get("players", []):
        if player["tracker_id"] == selected_track_id:
            return player
    players = metrics.get("players", [])
    if players:
        return players[0]
    return None
