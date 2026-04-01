"use client"

import { useState, use } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ChevronLeft, AlertCircle } from "lucide-react"
import { CourtCanvas } from "@/components/calibration/CourtCanvas"
import { submitCalibration, getFirstFrameUrl } from "@/lib/api"
import type { Corner } from "@/lib/types"

type PageProps = {
  params: Promise<{ id: string }>
}

export default function CalibratePage({ params }: PageProps) {
  const { id } = use(params)
  const router = useRouter()
  const [corners, setCorners] = useState<Corner[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [frameSize, setFrameSize] = useState<{
    width: number
    height: number
  } | null>(null)

  const imageUrl = getFirstFrameUrl(id)

  async function handleConfirm() {
    if (corners.length !== 4 || !frameSize) return

    setIsSubmitting(true)
    setError(null)

    try {
      const result = await submitCalibration(
        id,
        corners,
        frameSize.width,
        frameSize.height
      )

      if (!result.valid) {
        setError(
          "Calibração imprecisa. Tente selecionar os cantos com mais precisão."
        )
        setIsSubmitting(false)
        return
      }

      router.push(`/sessions/${id}/select-player`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao calibrar")
      setIsSubmitting(false)
    }
  }

  function handleReset() {
    setCorners([])
    setError(null)
  }

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Link
          href="/sessions"
          className="inline-flex items-center gap-1 text-gray-400 hover:text-gray-200 text-sm mb-6 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Sessões
        </Link>

        <h1 className="text-2xl font-bold text-white mb-2">Calibrar Quadra</h1>
        <p className="text-gray-400 text-sm mb-6">
          Clique nos 4 cantos da quadra em ordem:{" "}
          <span className="text-gray-300">
            canto superior esquerdo, superior direito, inferior direito, inferior
            esquerdo
          </span>
        </p>

        <div className="bg-gray-900 rounded-xl overflow-hidden mb-4">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4].map((n) => (
                <div
                  key={n}
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors ${
                    corners.length >= n
                      ? "bg-emerald-500 border-emerald-500 text-white"
                      : "bg-transparent border-gray-600 text-gray-500"
                  }`}
                >
                  {n}
                </div>
              ))}
              <span className="text-gray-400 text-xs ml-1">
                {corners.length}/4 cantos marcados
              </span>
            </div>
            <button
              onClick={handleReset}
              className="text-xs text-gray-400 hover:text-gray-200 transition-colors"
            >
              Refazer
            </button>
          </div>

          <CourtCanvas
            imageUrl={imageUrl}
            onCornersChange={setCorners}
            onFrameSizeDetected={setFrameSize}
          />
        </div>

        {error && (
          <div className="flex items-start gap-3 bg-red-950/40 border border-red-800 rounded-xl p-4 mb-4">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <p className="text-red-300 text-sm font-medium">
                Erro na calibração
              </p>
              <p className="text-red-400 text-sm mt-0.5">{error}</p>
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            onClick={() => void handleConfirm()}
            disabled={corners.length < 4 || isSubmitting}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-white font-medium px-6 py-2.5 rounded-lg transition-colors text-sm"
          >
            {isSubmitting ? "Calibrando..." : "Confirmar Calibração"}
          </button>
        </div>
      </div>
    </main>
  )
}
