"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Cpu, HardDrive, Activity } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminWorker } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"

export function AdminWorkers() {
  const { t } = useTranslation()
  const [workers, setWorkers] = useState<AdminWorker[]>([])
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
    apiFetch<AdminWorker[]>("/admin/workers")
      .then(setWorkers)
      .catch(() => setWorkers([]))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.workers")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.workers")}</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading workers...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.sidebar.workers")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.pages.workers")}</p>
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
                  <span>{worker.gpu_model || "—"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>{worker.gpu_vram_used_gb ?? "—"} / {worker.gpu_vram_total_gb ?? "—"} GB</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>CPU: {worker.cpu_usage_percent?.toFixed(0) ?? "—"}%</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Jobs today:</span> {worker.jobs_today}
                  {worker.failures_today > 0 && <span className="text-red-600 ml-2">({worker.failures_today} failed)</span>}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={async () => {
                    try {
                      await apiFetch(`/admin/workers/${worker.id}/restart`, { method: "POST" })
                      setWorkers(workers.map(w => w.id === worker.id ? { ...w, status: "restarting" } : w))
                    } catch (e: unknown) {
                      alert((e as Error)?.message || "Restart failed")
                    }
                  }}
                >
                  Restart
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={async () => {
                    if (!confirm(`Shutdown worker ${worker.name}?`)) return
                    try {
                      await apiFetch(`/admin/workers/${worker.id}/shutdown`, { method: "POST" })
                      setWorkers(workers.map(w => w.id === worker.id ? { ...w, status: "offline" } : w))
                    } catch (e: unknown) {
                      alert((e as Error)?.message || "Shutdown failed")
                    }
                  }}
                >
                  Shutdown
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {workers.length === 0 && (
          <p className="text-sm text-muted-foreground text-center col-span-2">No workers registered</p>
        )}
      </div>
    </div>
  )
}
