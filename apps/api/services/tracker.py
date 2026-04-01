from __future__ import annotations

import supervision as sv


class PlayerTracker:
    def __init__(self) -> None:
        self._tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=30,
            minimum_matching_threshold=0.8,
            frame_rate=30,
        )

    def update(self, detections: sv.Detections) -> sv.Detections:
        return self._tracker.update_with_detections(detections)

    def reset(self) -> None:
        self._tracker.reset()
