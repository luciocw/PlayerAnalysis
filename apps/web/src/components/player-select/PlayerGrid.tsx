"use client"

import { useState } from "react"
import Image from "next/image"
import { CheckCircle2, User } from "lucide-react"
import type { Player } from "@/lib/types"

type Props = {
  players: Player[]
  onSelect: (trackId: number) => void
  selectedTrackId: number | null
  isLoading: boolean
}

function PlayerThumbnail({
  player,
  isSelected,
  onClick,
}: {
  player: Player
  isSelected: boolean
  onClick: () => void
}) {
  const [imgError, setImgError] = useState(false)

  return (
    <button
      onClick={onClick}
      disabled={false}
      className={`relative rounded-xl overflow-hidden border-2 transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 ${
        isSelected
          ? "border-emerald-500 shadow-lg shadow-emerald-900/40"
          : "border-gray-700 hover:border-gray-500"
      }`}
    >
      <div className="aspect-[3/4] bg-gray-800 relative">
        {imgError ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-600">
            <User className="w-8 h-8" />
          </div>
        ) : (
          <Image
            src={player.thumbnail_url}
            alt={`Jogador #${player.track_id}`}
            fill
            className="object-cover"
            onError={() => setImgError(true)}
            unoptimized
          />
        )}

        {isSelected && (
          <div className="absolute inset-0 bg-emerald-900/30 flex items-center justify-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 drop-shadow" />
          </div>
        )}
      </div>

      <div className="px-2 py-1.5 bg-gray-900">
        <p
          className={`text-xs font-medium text-center truncate ${
            isSelected ? "text-emerald-400" : "text-gray-300"
          }`}
        >
          Jogador #{player.track_id}
        </p>
      </div>
    </button>
  )
}

export function PlayerGrid({
  players,
  onSelect,
  selectedTrackId,
  isLoading,
}: Props) {
  if (players.length === 0) {
    return (
      <div className="bg-gray-900 rounded-xl p-10 text-center">
        <User className="w-10 h-10 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400 text-sm">
          Nenhum jogador detectado no vídeo.
        </p>
      </div>
    )
  }

  return (
    <div
      className={`grid grid-cols-3 sm:grid-cols-4 gap-3 ${isLoading ? "opacity-50 pointer-events-none" : ""}`}
    >
      {players.map((player) => (
        <PlayerThumbnail
          key={player.track_id}
          player={player}
          isSelected={selectedTrackId === player.track_id}
          onClick={() => onSelect(player.track_id)}
        />
      ))}
    </div>
  )
}
