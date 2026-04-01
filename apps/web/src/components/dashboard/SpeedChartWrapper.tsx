"use client"

import type { SpeedPoint } from "@/lib/types"
import { SpeedChart } from "./SpeedChart"

type Props = {
  data: SpeedPoint[]
}

export function SpeedChartWrapper({ data }: Props) {
  return <SpeedChart data={data} />
}
