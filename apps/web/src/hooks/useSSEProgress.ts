"use client"

import { useEffect, useState } from "react"
import type { ProgressEvent } from "@/lib/types"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type SSEProgressState = {
  progress: ProgressEvent | null
  isDone: boolean
  isError: boolean
}

export function useSSEProgress(sessionId: string | null): SSEProgressState {
  const [state, setState] = useState<SSEProgressState>({
    progress: null,
    isDone: false,
    isError: false,
  })

  useEffect(() => {
    if (sessionId === null) return

    const source = new EventSource(`${BASE_URL}/progress/${sessionId}`)

    source.onmessage = (event: MessageEvent<string>) => {
      let parsed: ProgressEvent
      try {
        parsed = JSON.parse(event.data) as ProgressEvent
      } catch {
        return
      }

      setState((prev) => ({ ...prev, progress: parsed }))

      if (parsed.percent === 100) {
        setState({ progress: parsed, isDone: true, isError: false })
        source.close()
      } else if (parsed.percent === -1) {
        setState({ progress: parsed, isDone: false, isError: true })
        source.close()
      }
    }

    source.onerror = () => {
      setState((prev) => ({ ...prev, isError: true }))
      source.close()
    }

    return () => {
      source.close()
    }
  }, [sessionId])

  return state
}
