import type {
  CalibrationResult,
  Corner,
  Metrics,
  Player,
  Session,
} from "./types"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (typeof body === "object" && body !== null && "detail" in body) {
        message = String(body.detail)
      }
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(message)
  }
  return res.json() as Promise<T>
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${BASE_URL}/sessions`)
  return handleResponse<Session[]>(res)
}

export async function fetchSession(sessionId: string): Promise<Session> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}`)
  return handleResponse<Session>(res)
}

export async function fetchMetrics(sessionId: string): Promise<Metrics> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/metrics`)
  return handleResponse<Metrics>(res)
}

export async function fetchPlayers(sessionId: string): Promise<Player[]> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/players`)
  return handleResponse<Player[]>(res)
}

export async function submitCalibration(
  sessionId: string,
  corners: Corner[],
  frameWidth: number,
  frameHeight: number
): Promise<CalibrationResult> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/calibrate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ corners, frame_width: frameWidth, frame_height: frameHeight }),
  })
  return handleResponse<CalibrationResult>(res)
}

export async function selectPlayer(
  sessionId: string,
  trackId: number
): Promise<void> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/select-player`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track_id: trackId }),
  })
  await handleResponse<unknown>(res)
}

export async function triggerProcessing(sessionId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/process`, {
    method: "POST",
  })
  await handleResponse<unknown>(res)
}

export async function finalizeUpload(
  uploadId: string,
  totalChunks: number,
  originalFilename: string,
  fieldWidthM: number,
  fieldHeightM: number
): Promise<{ session_id: string }> {
  const res = await fetch(`${BASE_URL}/upload/finalize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      upload_id: uploadId,
      total_chunks: totalChunks,
      original_filename: originalFilename,
      field_width_m: fieldWidthM,
      field_height_m: fieldHeightM,
    }),
  })
  return handleResponse<{ session_id: string }>(res)
}

export function getFirstFrameUrl(sessionId: string): string {
  return `${BASE_URL}/sessions/${sessionId}/first-frame`
}

export function getHeatmapUrl(sessionId: string): string {
  return `${BASE_URL}/sessions/${sessionId}/heatmap`
}

export function getThumbnailUrl(sessionId: string, trackId: number): string {
  return `${BASE_URL}/sessions/${sessionId}/players/${trackId}/thumbnail`
}

export function exportPdfUrl(sessionId: string): string {
  return `${BASE_URL}/sessions/${sessionId}/export/pdf`
}
