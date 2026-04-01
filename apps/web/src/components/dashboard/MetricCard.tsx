import { cn } from "@/lib/utils"

type Props = {
  label: string
  value: string
  unit: string
  icon: React.ReactNode
  highlight?: boolean
}

export function MetricCard({ label, value, unit, icon, highlight = false }: Props) {
  return (
    <div
      className={cn(
        "bg-gray-900 rounded-xl p-4 flex flex-col gap-2",
        highlight && "ring-1 ring-emerald-700/50"
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center",
          highlight
            ? "bg-emerald-900/60 text-emerald-400"
            : "bg-gray-800 text-gray-400"
        )}
      >
        {icon}
      </div>

      <div>
        <p
          className={cn(
            "text-xl font-bold leading-none",
            highlight ? "text-emerald-400" : "text-white"
          )}
        >
          {value}
        </p>
        {unit && (
          <p className="text-xs text-gray-500 mt-0.5 leading-none">{unit}</p>
        )}
      </div>

      <p className="text-xs text-gray-400">{label}</p>
    </div>
  )
}
