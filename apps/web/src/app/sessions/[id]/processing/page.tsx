"use client"

import { useEffect, useState, use } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { AlertCircle, RefreshCw } from "lucide-react"
import { triggerProcessing } from "@/lib/api"
import { useSSEProgress } from "@/hooks/useSSEProgress"
import { formatDuration } from "@/lib/utils"

type PageProps = {
  params: Promise<{ id: string }>
}

export default function ProcessingPage({ params }: PageProps) {
  const { id } = use(params)
  const router = useRouter()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [triggerError, setTriggerError] = useState<string | null>(null)

  const { progress, isDone, isError } = useSSEProgress(sessionId)

  useEffect(() => {
    let cancelled = false

    async function start() {
      try {
        await triggerProcessing(id)
        if (!cancelled) {
          setSessionId(id)
        }
      } catch (err) {
        if (!cancelled) {
          setTriggerError(
            err instanceof Error ? err.message : "Erro ao iniciar processamento"
          )
        }
      }
    }

    void start()

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  useEffect(() => {
    if (isDone) {
      router.push(`/sessions/${id}/dashboard`)
    }
  }, [isDone, id, router])

  const percent = progress?.percent ?? 0
  const stage = progress?.stage ?? "Iniciando..."
  const etaSeconds = progress?.eta_seconds
  const framesDone = progress?.frames_done
  const framesTotal = progress?.frames_total

  if (triggerError) {
    return (
      <main className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-900 rounded-xl p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-white mb-2">
            Erro ao iniciar processamento
          </h2>
          <p className="text-gray-400 text-sm mb-6">{triggerError}</p>
          <Link
            href={`/sessions/${id}/select-player`}
            className="inline-flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-200 px-4 py-2 rounded-lg text-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Voltar e tentar novamente
          </Link>
        </div>
      </main>
    )
  }

  if (isError) {
    return (
      <main className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-900 rounded-xl p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-white mb-2">
            Erro no processamento
          </h2>
          <p className="text-gray-400 text-sm mb-2">
            {progress?.message ?? "Ocorreu um erro durante o processamento."}
          </p>
          <p className="text-gray-500 text-xs mb-6">
            Tente novamente ou entre em contato com o suporte.
          </p>
          <Link
            href="/sessions"
            className="inline-flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-200 px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Ver todas as sessões
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="max-w-lg w-full">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-emerald-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">⚙️</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Processando vídeo...
          </h1>
          <p className="text-gray-400 text-sm">
            Isso pode levar alguns minutos. Não feche esta página.
          </p>
        </div>

        <div className="bg-gray-900 rounded-xl p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-300">{stage}</span>
            <span className="text-sm font-bold text-emerald-400">
              {Math.round(percent)}%
            </span>
          </div>

          <div className="w-full bg-gray-800 rounded-full h-3 mb-5">
            <div
              className="bg-emerald-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(2, percent)}%` }}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {etaSeconds !== undefined && (
              <div className="bg-gray-800 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-0.5">Tempo estimado</p>
                <p className="text-sm font-semibold text-gray-200">
                  {formatDuration(etaSeconds)}
                </p>
              </div>
            )}

            {framesDone !== undefined && framesTotal !== undefined && (
              <div className="bg-gray-800 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-0.5">Frames</p>
                <p className="text-sm font-semibold text-gray-200">
                  {framesDone.toLocaleString("pt-BR")} /{" "}
                  {framesTotal.toLocaleString("pt-BR")}
                </p>
              </div>
            )}
          </div>

          {progress?.message && (
            <p className="text-xs text-gray-500 mt-4">{progress.message}</p>
          )}
        </div>
      </div>
    </main>
  )
}
