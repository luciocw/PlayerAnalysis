"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts"
import type { SpeedPoint } from "@/lib/types"
import { formatTime } from "@/lib/utils"

type Props = {
  data: SpeedPoint[]
}

const SPRINT_THRESHOLD_KMH = 18

function formatXAxis(value: number): string {
  return formatTime(value)
}

type TooltipPayload = {
  value: number
  dataKey: string
}

type CustomTooltipProps = {
  active?: boolean
  payload?: TooltipPayload[]
  label?: number
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null

  const speed = payload[0]?.value

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-gray-400 mb-1">
        {label !== undefined ? formatTime(label) : ""}
      </p>
      <p className="text-emerald-400 font-semibold">
        {speed !== undefined ? `${speed.toFixed(1)} km/h` : ""}
      </p>
    </div>
  )
}

export function SpeedChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-500 text-sm">
        Sem dados de velocidade disponíveis.
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="time_s"
          tickFormatter={formatXAxis}
          tick={{ fill: "#9ca3af", fontSize: 11 }}
          axisLine={{ stroke: "#374151" }}
          tickLine={{ stroke: "#374151" }}
          minTickGap={60}
        />
        <YAxis
          tick={{ fill: "#9ca3af", fontSize: 11 }}
          axisLine={{ stroke: "#374151" }}
          tickLine={{ stroke: "#374151" }}
          tickFormatter={(v: number) => `${v}`}
          width={32}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine
          y={SPRINT_THRESHOLD_KMH}
          stroke="#ef4444"
          strokeDasharray="5 3"
          label={{
            value: `Sprint (${SPRINT_THRESHOLD_KMH} km/h)`,
            fill: "#ef4444",
            fontSize: 10,
            position: "insideTopRight",
          }}
        />
        <Line
          type="monotone"
          dataKey="speed_kmh"
          stroke="#10b981"
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 4, fill: "#10b981" }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
