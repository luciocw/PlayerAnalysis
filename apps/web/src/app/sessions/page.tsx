import { Suspense } from "react"
import Link from "next/link"
import { PlusCircle } from "lucide-react"
import { SessionList } from "./SessionList"

export default function SessionsPage() {
  return (
    <main className="min-h-screen bg-gray-950">
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">
              Sessões de Análise
            </h1>
            <p className="text-gray-400 mt-1 text-sm">
              Gerencie e visualize as análises de vídeo
            </p>
          </div>
          <Link
            href="/sessions/new"
            className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
          >
            <PlusCircle className="w-4 h-4" />
            Nova Sessão
          </Link>
        </div>

        <Suspense fallback={<SessionListSkeleton />}>
          <SessionList />
        </Suspense>
      </div>
    </main>
  )
}

function SessionListSkeleton() {
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
