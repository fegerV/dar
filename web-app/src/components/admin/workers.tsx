"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Cpu, HardDrive, Activity } from "lucide-react"

const workers = [
  { id: "1", name: "video-worker-01", gpu: "RTX4090", vramTotal: 24, vramUsed: 21, cpu: 78, jobs: 2, status: "active" },
  { id: "2", name: "video-worker-02", gpu: "V100", vramTotal: 32, vramUsed: 28, cpu: 42, jobs: 1, status: "active" },
  { id: "3", name: "video-worker-03", gpu: "V100", vramTotal: 32, vramUsed: 31, cpu: 91, jobs: 1, status: "warning" },
  { id: "4", name: "worker-04", gpu: null, vramTotal: null, vramUsed: null, cpu: null, jobs: 0, status: "offline" },
]

export function AdminWorkers() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI / Workers</h1>
        <p className="text-muted-foreground mt-1">GPU workers and model status</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {workers.map((worker) => (
          <Card key={worker.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{worker.name}</CardTitle>
                <Badge className={
                  worker.status === "active" ? "bg-green-100 text-green-800" :
                  worker.status === "warning" ? "bg-yellow-100 text-yellow-800" :
                  "bg-red-100 text-red-800"
                }>
                  {worker.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>{worker.gpu || "—"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>{worker.vramUsed ?? "—"} / {worker.vramTotal ?? "—"} GB</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>CPU: {worker.cpu ?? "—"}%</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Jobs today:</span> {worker.jobs}
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1">Details</Button>
                <Button size="sm" variant="outline" className="flex-1">Restart</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
