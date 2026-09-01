"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminGeneration } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"

const statusColors: Record<string, string> = {
  SUCCESS: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
  RUNNING: "bg-blue-100 text-blue-800",
  PENDING: "bg-yellow-100 text-yellow-800",
}

export function AdminGenerations() {
  const { t } = useTranslation()
  const [generations, setGenerations] = useState<AdminGeneration[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<AdminGeneration[]>("/admin/generations")
      .then(setGenerations)
      .catch(() => setGenerations([]))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.generations")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.generations")}</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading generations...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.sidebar.generations")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.pages.generations")}</p>
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
                  <p className="font-medium">{gen.model_name || "—"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Project</p>
                  <p className="font-medium">{gen.project_id?.slice(0, 8)}…</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">{gen.duration_ms ? `${gen.duration_ms / 1000}s` : "—"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Cost</p>
                  <p className="font-medium">{gen.cost_rub} ₽</p>
                </div>
              </div>
              {gen.error_message && (
                <p className="mt-2 text-sm text-red-600">{gen.error_message}</p>
              )}
               <div className="mt-4 flex justify-end gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  aria-label={`View generation ${gen.id}`}
                  onClick={() => router.push(`/admin/generations/${gen.id}`)}
                >
                  View
                </Button>
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
