"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"
import { UploadZone } from "@/components/upload/UploadZone"

export default function NewSessionPage() {
  const router = useRouter()
  const [fieldWidthM, setFieldWidthM] = useState(40)
  const [fieldHeightM, setFieldHeightM] = useState(20)

  function handleUploadComplete(sessionId: string) {
    router.push(`/sessions/${sessionId}/calibrate`)
  }

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="max-w-2xl mx-auto px-4 py-10">
        <Link
          href="/sessions"
          className="inline-flex items-center gap-1 text-gray-400 hover:text-gray-200 text-sm mb-8 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Voltar
        </Link>

        <h1 className="text-2xl font-bold text-white mb-2">Nova Sessão</h1>
        <p className="text-gray-400 text-sm mb-8">
          Faça o upload de um vídeo de jogo para começar a análise.
        </p>

        <div className="bg-gray-900 rounded-xl p-6 mb-6">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-4">
            Dimensões da Quadra
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="field-width"
                className="block text-xs text-gray-400 mb-1.5"
              >
                Largura (metros)
              </label>
              <input
                id="field-width"
                type="number"
                min={10}
                max={60}
                value={fieldWidthM}
                onChange={(e) => setFieldWidthM(Number(e.target.value))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
            <div>
              <label
                htmlFor="field-height"
                className="block text-xs text-gray-400 mb-1.5"
              >
                Altura (metros)
              </label>
              <input
                id="field-height"
                type="number"
                min={10}
                max={40}
                value={fieldHeightM}
                onChange={(e) => setFieldHeightM(Number(e.target.value))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Quadra oficial de futsal: 40 × 20 m. Ajuste conforme necessário.
          </p>
        </div>

        <UploadZone
          onUploadComplete={handleUploadComplete}
          fieldWidthM={fieldWidthM}
          fieldHeightM={fieldHeightM}
        />
      </div>
    </main>
  )
}
