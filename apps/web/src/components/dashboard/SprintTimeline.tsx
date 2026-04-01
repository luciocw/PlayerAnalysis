import type { Sprint } from "@/lib/types"
import { formatTime, formatDistance, formatSpeed } from "@/lib/utils"
import { Zap } from "lucide-react"

type Props = {
  sprints: Sprint[]
}

export function SprintTimeline({ sprints }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-4 h-4 text-yellow-400" />
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
          Arrancadas
        </h2>
        {sprints.length > 0 && (
          <span className="ml-auto text-xs text-gray-500">
            {sprints.length} registrada{sprints.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {sprints.length === 0 ? (
        <p className="text-gray-500 text-sm py-4 text-center">
          Nenhuma arrancada registrada.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-gray-800">
                <th className="text-left pb-2 pr-4 font-medium">#</th>
                <th className="text-left pb-2 pr-4 font-medium">Tempo</th>
                <th className="text-left pb-2 pr-4 font-medium">Duração</th>
                <th className="text-left pb-2 pr-4 font-medium">Distância</th>
                <th className="text-left pb-2 font-medium">Vel. Máx</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {sprints.map((sprint, i) => {
                const duration = sprint.end_s - sprint.start_s
                return (
                  <tr key={i} className="text-gray-300">
                    <td className="py-2.5 pr-4 text-gray-500 text-xs">
                      {i + 1}
                    </td>
                    <td className="py-2.5 pr-4 font-mono text-xs">
                      {formatTime(sprint.start_s)}
                    </td>
                    <td className="py-2.5 pr-4 text-xs">
                      {duration.toFixed(1)}s
                    </td>
                    <td className="py-2.5 pr-4 text-xs">
                      {formatDistance(sprint.distance_m)}
                    </td>
                    <td className="py-2.5">
                      <span className="text-yellow-400 font-semibold text-xs">
                        {formatSpeed(sprint.max_speed_kmh)}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
