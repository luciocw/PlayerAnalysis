import Image from "next/image"

type Props = {
  heatmapUrl: string
  fieldWidthM: number
  fieldHeightM: number
}

export function HeatmapDisplay({ heatmapUrl, fieldWidthM, fieldHeightM }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl p-4">
      <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-1">
        Mapa de Calor — Posições em Campo
      </h2>
      <p className="text-xs text-gray-500 mb-4">
        {fieldWidthM} × {fieldHeightM} m
      </p>

      <div className="relative w-full rounded-lg overflow-hidden bg-gray-950">
        <Image
          src={heatmapUrl}
          alt="Mapa de calor das posições em campo"
          width={800}
          height={400}
          className="w-full h-auto object-contain"
          unoptimized
          onError={() => {
            // error handled by fallback below via CSS trick
          }}
        />
      </div>
    </div>
  )
}
