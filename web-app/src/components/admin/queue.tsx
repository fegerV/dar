"use client"

import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Play, Pause, RotateCcw, X, ArrowUp, ArrowDown } from "lucide-react"

const runningJobs = [
  { id: "89213", model: "Kling", progress: 72 },
  { id: "89212", model: "Veo", progress: 41 },
]

const pendingJobs = [
  { id: "89214", model: "Kling" },
  { id: "89215", model: "Wan" },
  { id: "89216", model: "Veo" },
  { id: "89217", model: "Kling" },
]

export function AdminQueue() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Generation Queue</h1>
        <p className="text-muted-foreground mt-1">Dispatch and monitor generation jobs</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Running</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {runningJobs.map((job) => (
              <div key={job.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-medium">#{job.id}</span>
                  <span className="text-sm text-muted-foreground">{job.model}</span>
                </div>
                <Progress value={job.progress} aria-label={`Job ${job.id} progress ${job.progress}%`} />
                <div className="mt-3 flex gap-2">
                  <Button size="sm" variant="outline" aria-label={`Pause job ${job.id}`}>
                    <Pause className="h-4 w-4" aria-hidden="true" />
                  </Button>
                  <Button size="sm" variant="outline" aria-label={`Cancel job ${job.id}`}>
                    <X className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {pendingJobs.map((job, idx) => (
                <div key={job.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <span className="font-mono font-medium">#{job.id}</span>
                    <span className="ml-3 text-sm text-muted-foreground">{job.model}</span>
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" aria-label={`Move job ${job.id} to front`}>
                      <ArrowUp className="h-4 w-4" aria-hidden="true" />
                    </Button>
                    <Button size="sm" variant="ghost" aria-label={`Move job ${job.id} down`}>
                      <ArrowDown className="h-4 w-4" aria-hidden="true" />
                    </Button>
                    <Button size="sm" variant="ghost" aria-label={`Retry job ${job.id}`}>
                      <RotateCcw className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
