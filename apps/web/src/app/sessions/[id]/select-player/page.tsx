"use client"

import { useState, use } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { ChevronLeft, AlertCircle, Loader2 } from "lucide-react"
import { fetchPlayers, selectPlayer } from "@/lib/api"
import { PlayerGrid } from "@/components/player-select/PlayerGrid"

type PageProps = {
  params: Promise<{ id: string }>
}

export default function SelectPlayerPage({ params }: PageProps) {
  const { id } = use(params)
  const router = useRouter()
  const [selectedTrackId, setSelectedTrackId] = useState<number | null>(null)
  const [isConfirming, setIsConfirming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { data: players, isLoading, isError, error: queryError } = useQuery({
    queryKey: ["players", id],
    queryFn: () => fetchPlayers(id),
  })

  async function handleConfirm() {
    if (selectedTrackId === null) return

    setIsConfirming(true)
    setError(null)

    try {
      await selectPlayer(id, selectedTrackId)
      router.push(`/sessions/${id}/processing`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao selecionar jogador")
      setIsConfirming(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Link
          href={`/sessions/${id}/calibrate`}
          className="inline-flex items-center gap-1 text-gray-400 hover:text-gray-200 text-sm mb-6 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Calibração
        </Link>

        <h1 className="text-2xl font-bold text-white mb-2">
          Qual é o seu filho?
        </h1>
        <p className="text-gray-400 text-sm mb-8">
          Selecione o jogador para acompanhar durante a partida.
        </p>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-3" />
              <p className="text-gray-400 text-sm">
                Analisando jogadores detectados no vídeo...
              </p>
            </div>
          </div>
        )}

        {isError && (
          <div className="flex items-start gap-3 bg-red-950/40 border border-red-800 rounded-xl p-4 mb-6">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <p className="text-red-300 text-sm">
              {queryError instanceof Error
                ? queryError.message
                : "Erro ao carregar jogadores"}
            </p>
          </div>
        )}

        {players && (
          <>
            <PlayerGrid
              players={players}
              onSelect={setSelectedTrackId}
              selectedTrackId={selectedTrackId}
              isLoading={isConfirming}
            />

            {error && (
              <div className="mt-4 flex items-start gap-3 bg-red-950/40 border border-red-800 rounded-xl p-4">
                <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <div className="flex justify-end mt-6">
              <button
                onClick={() => void handleConfirm()}
                disabled={selectedTrackId === null || isConfirming}
                className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-white font-medium px-6 py-2.5 rounded-lg transition-colors text-sm"
              >
                {isConfirming ? "Confirmando..." : "Analisar esse jogador"}
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
