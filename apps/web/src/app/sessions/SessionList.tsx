"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { fetchSessions } from "@/lib/api"
import type { Session, SessionStatus } from "@/lib/types"
import { formatDuration } from "@/lib/utils"
import { ChevronRight, AlertCircle, RefreshCw } from "lucide-react"

const STATUS_LABELS: Record<SessionStatus, string> = {
  uploaded: "Enviado",
  calibrated: "Calibrado",
  player_selected: "Jogador Selecionado",
  processing: "Processando",
  done: "Concluído",
  error: "Erro",
}

const STATUS_CLASSES: Record<SessionStatus, string> = {
  uploaded: "bg-gray-700 text-gray-300",
  calibrated: "bg-blue-900 text-blue-300",
  player_selected: "bg-purple-900 text-purple-300",
  processing: "bg-yellow-900 text-yellow-300 animate-pulse",
  done: "bg-emerald-900 text-emerald-300",
  error: "bg-red-900 text-red-300",
}

function getSessionHref(session: Session): string | null {
  switch (session.status) {
    case "uploaded":
      return `/sessions/${session.session_id}/calibrate`
    case "calibrated":
      return `/sessions/${session.session_id}/select-player`
    case "player_selected":
      return `/sessions/${session.session_id}/processing`
    case "processing":
      return `/sessions/${session.session_id}/processing`
    case "done":
      return `/sessions/${session.session_id}/dashboard`
    case "error":
      return null
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function SessionRow({ session }: { session: Session }) {
  const href = getSessionHref(session)

  const inner = (
    <div className="bg-gray-900 rounded-xl p-4 flex items-center justify-between gap-4 hover:bg-gray-800/80 transition-colors">
      <div className="flex-1 min-w-0">
        <p className="font-medium text-white truncate">
          {session.original_filename}
        </p>
        <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
          <span>{formatDate(session.created_at)}</span>
          {session.duration_seconds !== null && (
            <span>{formatDuration(session.duration_seconds)}</span>
          )}
          <span>
            {session.field_width_m}x{session.field_height_m} m
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <span
          className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_CLASSES[session.status]}`}
        >
          {STATUS_LABELS[session.status]}
        </span>
        {href && <ChevronRight className="w-4 h-4 text-gray-500" />}
      </div>
    </div>
  )

  if (!href) {
    return <div className="cursor-default">{inner}</div>
  }

  return <Link href={href}>{inner}</Link>
}

export function SessionList() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["sessions"],
    queryFn: fetchSessions,
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-gray-900 rounded-xl p-4 animate-pulse flex items-center justify-between"
          >
            <div className="space-y-2">
              <div className="h-4 w-48 bg-gray-700 rounded" />
              <div className="h-3 w-32 bg-gray-800 rounded" />
            </div>
            <div className="h-6 w-20 bg-gray-700 rounded-full" />
          </div>
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-red-950/40 border border-red-800 rounded-xl p-6 text-center">
        <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
        <p className="text-red-300 font-medium mb-1">
          Erro ao carregar sessões
        </p>
        <p className="text-red-400 text-sm mb-4">
          {error instanceof Error ? error.message : "Erro desconhecido"}
        </p>
        <button
          onClick={() => void refetch()}
          className="inline-flex items-center gap-2 text-sm text-red-300 hover:text-red-200"
        >
          <RefreshCw className="w-4 h-4" />
          Tentar novamente
        </button>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-900 rounded-xl p-12 text-center">
        <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">⚽</span>
        </div>
        <p className="text-gray-300 font-medium mb-1">Nenhuma sessão ainda</p>
        <p className="text-gray-500 text-sm">
          Comece fazendo upload de um vídeo.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((session) => (
        <SessionRow key={session.session_id} session={session} />
      ))}
    </div>
  )
}
