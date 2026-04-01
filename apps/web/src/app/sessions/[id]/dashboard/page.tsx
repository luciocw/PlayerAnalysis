import { Suspense, use } from "react"
import Link from "next/link"
import { ChevronLeft, Download, Activity, Zap, TrendingUp, Timer } from "lucide-react"
import { fetchSession, fetchMetrics, exportPdfUrl } from "@/lib/api"
import { formatDistance, formatSpeed, formatDuration } from "@/lib/utils"
import { MetricCard } from "@/components/dashboard/MetricCard"
import { SpeedChartWrapper } from "@/components/dashboard/SpeedChartWrapper"
import { HeatmapDisplay } from "@/components/dashboard/HeatmapDisplay"
import { SprintTimeline } from "@/components/dashboard/SprintTimeline"

type PageProps = {
  params: Promise<{ id: string }>
}

async function DashboardContent({ id }: { id: string }) {
  const [session, metrics] = await Promise.all([
    fetchSession(id),
    fetchMetrics(id),
  ])

  const pdfUrl = exportPdfUrl(id)

  return (
    <>
      <div className="flex items-start justify-between mb-8 gap-4">
        <div className="min-w-0">
          <Link
            href="/sessions"
            className="inline-flex items-center gap-1 text-gray-400 hover:text-gray-200 text-sm mb-3 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Sessões
          </Link>
          <h1 className="text-xl font-bold text-white truncate">
            Análise — {session.original_filename}
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Duração: {formatDuration(metrics.duration_seconds)}
          </p>
        </div>

        <a
          href={pdfUrl}
          download
          className="shrink-0 inline-flex items-center gap-2 bg-emerald-700 hover:bg-emerald-600 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Download className="w-4 h-4" />
          Exportar PDF
        </a>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <MetricCard
          label="Distância Total"
          value={formatDistance(metrics.total_distance_m)}
          unit=""
          icon={<Activity className="w-5 h-5" />}
          highlight
        />
        <MetricCard
          label="Vel. Média"
          value={formatSpeed(metrics.avg_speed_kmh)}
          unit=""
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <MetricCard
          label="Vel. Máxima"
          value={formatSpeed(metrics.max_speed_kmh)}
          unit=""
          icon={<Zap className="w-5 h-5" />}
        />
        <MetricCard
          label="Arrancadas"
          value={String(metrics.sprint_count)}
          unit={`${formatDistance(metrics.sprint_total_distance_m)} total`}
          icon={<Timer className="w-5 h-5" />}
        />
      </div>

      <div className="mb-6">
        <HeatmapDisplay
          heatmapUrl={metrics.heatmap_url}
          fieldWidthM={session.field_width_m}
          fieldHeightM={session.field_height_m}
        />
      </div>

      <div className="mb-6">
        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-4">
            Velocidade ao Longo do Jogo
          </h2>
          <SpeedChartWrapper data={metrics.speed_series} />
        </div>
      </div>

      <SprintTimeline sprints={metrics.sprints} />
    </>
  )
}

function DashboardSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 w-64 bg-gray-800 rounded" />
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-gray-900 rounded-xl h-24" />
        ))}
      </div>
      <div className="bg-gray-900 rounded-xl h-64" />
      <div className="bg-gray-900 rounded-xl h-48" />
    </div>
  )
}

export default function DashboardPage({ params }: PageProps) {
  const { id } = use(params)

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Suspense fallback={<DashboardSkeleton />}>
          <DashboardContent id={id} />
        </Suspense>
      </div>
    </main>
  )
}
