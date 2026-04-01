export type SessionStatus =
  | "uploaded"
  | "calibrated"
  | "player_selected"
  | "processing"
  | "done"
  | "error"

export type Session = {
  session_id: string
  original_filename: string
  created_at: string
  status: SessionStatus
  duration_seconds: number | null
  field_width_m: number
  field_height_m: number
}

export type Corner = { x: number; y: number }

export type CalibrationResult = {
  homography_matrix: number[][]
  reprojection_error: number
  valid: boolean
}

export type Player = {
  track_id: number
  thumbnail_url: string
}

export type SpeedPoint = { time_s: number; speed_kmh: number }

export type Sprint = {
  start_s: number
  end_s: number
  distance_m: number
  max_speed_kmh: number
}

export type Metrics = {
  session_id: string
  total_distance_m: number
  avg_speed_kmh: number
  max_speed_kmh: number
  sprint_count: number
  sprint_total_distance_m: number
  duration_seconds: number
  speed_series: SpeedPoint[]
  heatmap_url: string
  sprints: Sprint[]
}

export type ProgressEvent = {
  percent: number
  stage: string
  eta_seconds?: number
  frames_done?: number
  frames_total?: number
  message?: string
}
