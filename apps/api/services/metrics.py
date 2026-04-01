from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import supervision as sv

from .homography import pixel_to_meters


@dataclass
class PlayerMetrics:
    tracker_id: int
    label: str
    positions_m: List[Tuple[float, float]] = field(default_factory=list)
    timestamps_s: List[float] = field(default_factory=list)
    speeds_kmh: List[float] = field(default_factory=list)
    total_distance_m: float = 0.0
    max_speed_kmh: float = 0.0
    sprint_count: int = 0
    sprint_total_distance_m: float = 0.0
    sprints: List[dict] = field(default_factory=list)


class MetricsAccumulator:
    _SPEED_WINDOW = 5

    def __init__(
        self,
        fps: float,
        H: np.ndarray,
        sample_rate: int,
        sprint_speed_kmh: float,
        sprint_min_frames: int,
    ) -> None:
        self._fps = fps
        self._H = H
        self._sample_rate = sample_rate
        self._sprint_speed_kmh = sprint_speed_kmh
        self._sprint_min_frames = sprint_min_frames
        self._effective_fps = fps / sample_rate
        self._dt = 1.0 / self._effective_fps

        self._players: Dict[int, PlayerMetrics] = {}
        self._speed_buffers: Dict[int, Deque[float]] = defaultdict(
            lambda: deque(maxlen=self._SPEED_WINDOW)
        )
        self._sprint_consecutive: Dict[int, int] = defaultdict(int)
        self._active_sprint: Dict[int, Optional[dict]] = defaultdict(lambda: None)

    def get_foot_point(self, xyxy: np.ndarray) -> Tuple[float, float]:
        x1, y1, x2, y2 = xyxy
        cx = (x1 + x2) / 2.0
        return float(cx), float(y2)

    def update(self, tracked_detections: sv.Detections, frame_number: int) -> None:
        if tracked_detections.tracker_id is None:
            return

        timestamp_s = frame_number / self._fps

        for i, track_id in enumerate(tracked_detections.tracker_id):
            track_id = int(track_id)
            xyxy = tracked_detections.xyxy[i]
            foot_px = self.get_foot_point(xyxy)
            pos_m = pixel_to_meters(self._H, foot_px)

            if track_id not in self._players:
                self._players[track_id] = PlayerMetrics(
                    tracker_id=track_id,
                    label=f"Jogador {track_id}",
                )

            player = self._players[track_id]

            if len(player.positions_m) > 0:
                prev_pos = player.positions_m[-1]
                delta_m = float(
                    np.linalg.norm(
                        np.array(pos_m) - np.array(prev_pos)
                    )
                )
                speed_ms = delta_m / self._dt
                speed_kmh = speed_ms * 3.6

                self._speed_buffers[track_id].append(speed_kmh)
                smoothed_speed = float(np.mean(self._speed_buffers[track_id]))

                player.total_distance_m += delta_m
                player.speeds_kmh.append(smoothed_speed)

                if smoothed_speed > player.max_speed_kmh:
                    player.max_speed_kmh = smoothed_speed

                self._update_sprint(track_id, player, smoothed_speed, timestamp_s, delta_m)
            else:
                player.speeds_kmh.append(0.0)

            player.positions_m.append(pos_m)
            player.timestamps_s.append(timestamp_s)

    def _update_sprint(
        self,
        track_id: int,
        player: PlayerMetrics,
        speed_kmh: float,
        timestamp_s: float,
        delta_m: float,
    ) -> None:
        if speed_kmh >= self._sprint_speed_kmh:
            self._sprint_consecutive[track_id] += 1

            if self._active_sprint[track_id] is None:
                self._active_sprint[track_id] = {
                    "start_s": timestamp_s,
                    "end_s": timestamp_s,
                    "distance_m": delta_m,
                    "max_speed_kmh": speed_kmh,
                }
            else:
                sprint = self._active_sprint[track_id]
                sprint["end_s"] = timestamp_s
                sprint["distance_m"] += delta_m
                if speed_kmh > sprint["max_speed_kmh"]:
                    sprint["max_speed_kmh"] = speed_kmh
        else:
            consecutive = self._sprint_consecutive[track_id]
            if (
                consecutive >= self._sprint_min_frames
                and self._active_sprint[track_id] is not None
            ):
                sprint = self._active_sprint[track_id]
                player.sprints.append(sprint)
                player.sprint_count += 1
                player.sprint_total_distance_m += sprint["distance_m"]

            self._sprint_consecutive[track_id] = 0
            self._active_sprint[track_id] = None

    def _close_open_sprints(self) -> None:
        for track_id, consecutive in self._sprint_consecutive.items():
            if (
                consecutive >= self._sprint_min_frames
                and self._active_sprint[track_id] is not None
            ):
                player = self._players.get(track_id)
                if player is None:
                    continue
                sprint = self._active_sprint[track_id]
                player.sprints.append(sprint)
                player.sprint_count += 1
                player.sprint_total_distance_m += sprint["distance_m"]
                self._active_sprint[track_id] = None

    def finalize(self) -> dict:
        self._close_open_sprints()

        players_out = []
        for player in self._players.values():
            avg_speed = (
                float(np.mean(player.speeds_kmh)) if player.speeds_kmh else 0.0
            )
            players_out.append(
                {
                    "tracker_id": player.tracker_id,
                    "label": player.label,
                    "total_distance_m": round(player.total_distance_m, 2),
                    "max_speed_kmh": round(player.max_speed_kmh, 2),
                    "avg_speed_kmh": round(avg_speed, 2),
                    "sprint_count": player.sprint_count,
                    "sprint_total_distance_m": round(player.sprint_total_distance_m, 2),
                    "sprints": [
                        {
                            "start_s": round(s["start_s"], 2),
                            "end_s": round(s["end_s"], 2),
                            "distance_m": round(s["distance_m"], 2),
                            "max_speed_kmh": round(s["max_speed_kmh"], 2),
                        }
                        for s in player.sprints
                    ],
                    "speed_series": [round(v, 2) for v in player.speeds_kmh],
                    "timestamps_s": [round(t, 3) for t in player.timestamps_s],
                    "positions_m": [
                        {"x": round(p[0], 3), "y": round(p[1], 3)}
                        for p in player.positions_m
                    ],
                }
            )

        return {"players": players_out}

    def get_summary_dataframe(self) -> pd.DataFrame:
        rows = []
        for player in self._players.values():
            avg_speed = (
                float(np.mean(player.speeds_kmh)) if player.speeds_kmh else 0.0
            )
            rows.append(
                {
                    "tracker_id": player.tracker_id,
                    "label": player.label,
                    "total_distance_m": round(player.total_distance_m, 2),
                    "max_speed_kmh": round(player.max_speed_kmh, 2),
                    "avg_speed_kmh": round(avg_speed, 2),
                    "sprint_count": player.sprint_count,
                    "sprint_total_distance_m": round(player.sprint_total_distance_m, 2),
                }
            )
        return pd.DataFrame(rows)
