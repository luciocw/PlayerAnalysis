"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import type { Corner } from "@/lib/types"

type Props = {
  imageUrl: string
  onCornersChange: (corners: Corner[]) => void
  onFrameSizeDetected: (size: { width: number; height: number }) => void
}

const MARKER_RADIUS = 10
const MARKER_COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e"]

export function CourtCanvas({
  imageUrl,
  onCornersChange,
  onFrameSizeDetected,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement | null>(null)
  const [corners, setCorners] = useState<Corner[]>([])
  const [canvasSize, setCanvasSize] = useState<{
    width: number
    height: number
  } | null>(null)
  const [naturalSize, setNaturalSize] = useState<{
    width: number
    height: number
  } | null>(null)
  const [loadError, setLoadError] = useState(false)

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current
    const img = imageRef.current
    if (!canvas || !img || !canvasSize) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

    // Draw connecting lines between corners
    if (corners.length >= 2) {
      ctx.strokeStyle = "rgba(16, 185, 129, 0.7)"
      ctx.lineWidth = 2
      ctx.setLineDash([6, 3])
      ctx.beginPath()

      const displayCorners = corners.map((c) => toDisplay(c, canvasSize, naturalSize!))
      ctx.moveTo(displayCorners[0].x, displayCorners[0].y)
      for (let i = 1; i < displayCorners.length; i++) {
        ctx.lineTo(displayCorners[i].x, displayCorners[i].y)
      }
      if (corners.length === 4) {
        ctx.closePath()
      }
      ctx.stroke()
      ctx.setLineDash([])
    }

    // Draw markers
    corners.forEach((corner, i) => {
      const display = toDisplay(corner, canvasSize, naturalSize!)
      const color = MARKER_COLORS[i] ?? "#ffffff"

      // Outer ring
      ctx.beginPath()
      ctx.arc(display.x, display.y, MARKER_RADIUS, 0, Math.PI * 2)
      ctx.fillStyle = `${color}33`
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.stroke()

      // Inner dot
      ctx.beginPath()
      ctx.arc(display.x, display.y, 4, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.fill()

      // Number label
      ctx.fillStyle = "#ffffff"
      ctx.font = "bold 11px system-ui"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"
      ctx.fillText(String(i + 1), display.x, display.y - MARKER_RADIUS - 8)
    })
  }, [corners, canvasSize, naturalSize])

  function toDisplay(
    corner: Corner,
    canvas: { width: number; height: number },
    natural: { width: number; height: number }
  ): { x: number; y: number } {
    return {
      x: (corner.x / natural.width) * canvas.width,
      y: (corner.y / natural.height) * canvas.height,
    }
  }

  function toNatural(
    displayX: number,
    displayY: number,
    canvas: { width: number; height: number },
    natural: { width: number; height: number }
  ): Corner {
    return {
      x: Math.round((displayX / canvas.width) * natural.width),
      y: Math.round((displayY / canvas.height) * natural.height),
    }
  }

  // Load image once
  useEffect(() => {
    const img = new Image()
    img.crossOrigin = "anonymous"

    img.onload = () => {
      imageRef.current = img
      const nat = { width: img.naturalWidth, height: img.naturalHeight }
      setNaturalSize(nat)
      onFrameSizeDetected(nat)
    }

    img.onerror = () => {
      setLoadError(true)
    }

    img.src = imageUrl
  }, [imageUrl, onFrameSizeDetected])

  // Resize canvas to fit container
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !naturalSize) return

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (!entry) return

      const containerWidth = entry.contentRect.width
      const aspectRatio = naturalSize.height / naturalSize.width
      const newHeight = Math.round(containerWidth * aspectRatio)

      canvas.width = containerWidth
      canvas.height = newHeight
      setCanvasSize({ width: containerWidth, height: newHeight })
    })

    observer.observe(canvas.parentElement ?? canvas)
    return () => observer.disconnect()
  }, [naturalSize])

  // Redraw whenever state changes
  useEffect(() => {
    drawCanvas()
  }, [drawCanvas])

  function handleClick(e: React.MouseEvent<HTMLCanvasElement>) {
    if (corners.length >= 4) return
    if (!canvasRef.current || !canvasSize || !naturalSize) return

    const rect = canvasRef.current.getBoundingClientRect()
    const scaleX = canvasSize.width / rect.width
    const scaleY = canvasSize.height / rect.height

    const clickX = (e.clientX - rect.left) * scaleX
    const clickY = (e.clientY - rect.top) * scaleY

    const newCorner = toNatural(clickX, clickY, canvasSize, naturalSize)
    const newCorners = [...corners, newCorner]

    setCorners(newCorners)
    onCornersChange(newCorners)
  }

  if (loadError) {
    return (
      <div className="flex items-center justify-center h-48 bg-gray-950 text-gray-500 text-sm">
        Não foi possível carregar o primeiro frame.
      </div>
    )
  }

  return (
    <div className="relative w-full bg-gray-950">
      <canvas
        ref={canvasRef}
        onClick={handleClick}
        className="w-full block cursor-crosshair"
        style={{ touchAction: "none" }}
      />
      {!naturalSize && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-950">
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <div className="w-4 h-4 border-2 border-gray-600 border-t-emerald-500 rounded-full animate-spin" />
            Carregando frame...
          </div>
        </div>
      )}
    </div>
  )
}
