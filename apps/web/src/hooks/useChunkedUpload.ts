"use client"

import { useState } from "react"
import { finalizeUpload } from "@/lib/api"

const CHUNK_SIZE = 10 * 1024 * 1024 // 10 MB
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type UploadState = {
  progress: number
  isUploading: boolean
  error: string | null
}

type UseChunkedUploadReturn = UploadState & {
  upload: (
    file: File,
    fieldWidthM: number,
    fieldHeightM: number
  ) => Promise<string>
}

function uploadChunk(
  uploadId: string,
  chunkIndex: number,
  totalChunks: number,
  chunk: Blob,
  filename: string,
  onProgress: (loaded: number, total: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append("upload_id", uploadId)
    formData.append("chunk_index", String(chunkIndex))
    formData.append("total_chunks", String(totalChunks))
    formData.append("file", chunk, filename)

    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable) {
        onProgress(e.loaded, e.total)
      }
    })

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        let message = `HTTP ${xhr.status}`
        try {
          const body = JSON.parse(xhr.responseText) as Record<string, unknown>
          if (typeof body.detail === "string") {
            message = body.detail
          }
        } catch {
          // ignore
        }
        reject(new Error(message))
      }
    })

    xhr.addEventListener("error", () => {
      reject(new Error("Network error during chunk upload"))
    })

    xhr.open("POST", `${BASE_URL}/upload/chunk`)
    xhr.send(formData)
  })
}

export function useChunkedUpload(): UseChunkedUploadReturn {
  const [state, setState] = useState<UploadState>({
    progress: 0,
    isUploading: false,
    error: null,
  })

  async function upload(
    file: File,
    fieldWidthM: number,
    fieldHeightM: number
  ): Promise<string> {
    setState({ progress: 0, isUploading: true, error: null })

    const uploadId = crypto.randomUUID()
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE)

    try {
      for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, file.size)
        const chunk = file.slice(start, end)

        await uploadChunk(
          uploadId,
          i,
          totalChunks,
          chunk,
          file.name,
          (loaded, total) => {
            const chunkFraction = loaded / total
            const overallProgress = ((i + chunkFraction) / totalChunks) * 100
            setState((prev) => ({ ...prev, progress: overallProgress }))
          }
        )

        // Update progress after each chunk completes
        setState((prev) => ({
          ...prev,
          progress: ((i + 1) / totalChunks) * 100,
        }))
      }

      const result = await finalizeUpload(
        uploadId,
        totalChunks,
        file.name,
        fieldWidthM,
        fieldHeightM
      )

      setState({ progress: 100, isUploading: false, error: null })
      return result.session_id
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload falhou"
      setState({ progress: 0, isUploading: false, error: message })
      throw err
    }
  }

  return { ...state, upload }
}
