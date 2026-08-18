"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Play } from "lucide-react"

const generations = [
  { id: "89213", model: "Kling 3", workflow: "birthday_v4", status: "SUCCESS", duration: "87 sec", cost: "$0.81" },
  { id: "89212", model: "Veo", workflow: "portrait_v2", status: "FAILED", duration: "12 sec", cost: "$0.45" },
  { id: "89211", model: "Grok", workflow: "cinematic_v1", status: "SUCCESS", duration: "64 sec", cost: "$0.62" },
]

const statusColors: Record<string, string> = {
  SUCCESS: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
  RUNNING: "bg-blue-100 text-blue-800",
  PENDING: "bg-yellow-100 text-yellow-800",
}

export function AdminGenerations() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Generations</h1>
        <p className="text-muted-foreground mt-1">All generation attempts and their details</p>
      </div>

      <div className="grid gap-4">
        {generations.map((gen) => (
          <Card key={gen.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Generation #{gen.id}</CardTitle>
                <Badge className={statusColors[gen.status] || "bg-gray-100"}>{gen.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Model</p>
                  <p className="font-medium">{gen.model}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Workflow</p>
                  <p className="font-medium">{gen.workflow}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">{gen.duration}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Cost</p>
                  <p className="font-medium">{gen.cost}</p>
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <Button size="sm" variant="outline" aria-label={`Play video for generation ${gen.id}`}>
                  <Play className="h-4 w-4 mr-2" aria-hidden="true" />
                  Play Video
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
