"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import type { AdminWorkerDetailResponse } from "@/types/admin"

export default function AdminWorkerDetailPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [worker, setWorker] = useState<AdminWorkerDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadWorker = useCallback(async () => {
    if (!user || !params.id) return
    setLoading(true)
    try {
      const data = await apiFetch<AdminWorkerDetailResponse>(`/admin/workers/${params.id}`)
      setWorker(data)
    } catch {
      setWorker(null)
    } finally {
      setLoading(false)
    }
  }, [user, params.id])

  useEffect(() => {
    if (user && params.id) loadWorker()
  }, [user, params.id, loadWorker])

  const updateStatus = async (status: string) => {
    if (!worker) return
    setUpdating(true)
    try {
      await apiFetch(`/admin/workers/${worker.id}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      })
      await loadWorker()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Status update failed")
    } finally {
      setUpdating(false)
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading worker...</p>
  }

  if (!worker) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.workers")}</h1>
          <p className="text-muted-foreground mt-1">{worker.name}</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Worker Details</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p><span className="text-muted-foreground">ID:</span> <span className="font-mono">{worker.id}</span></p>
          <p><span className="text-muted-foreground">Name:</span> {worker.name}</p>
          <p><span className="text-muted-foreground">Status:</span> <Badge>{worker.status}</Badge></p>
          <p><span className="text-muted-foreground">GPU Model:</span> {worker.gpu_model || "—"}</p>
          <p><span className="text-muted-foreground">GPU VRAM Total:</span> {worker.gpu_vram_total_gb ?? "—"} GB</p>
          <p><span className="text-muted-foreground">GPU VRAM Used:</span> {worker.gpu_vram_used_gb ?? "—"} GB</p>
          <p><span className="text-muted-foreground">CPU Usage:</span> {worker.cpu_usage_percent ?? "—"}%</p>
          <p><span className="text-muted-foreground">Jobs Today:</span> {worker.jobs_today}</p>
          <p><span className="text-muted-foreground">Failures Today:</span> {worker.failures_today}</p>
          <p><span className="text-muted-foreground">Avg Generation Time:</span> {worker.avg_generation_time_sec ? `${worker.avg_generation_time_sec.toFixed(1)}s` : "—"}</p>
          <p><span className="text-muted-foreground">Last Heartbeat:</span> {worker.last_heartbeat_at ? new Date(worker.last_heartbeat_at).toLocaleString() : "—"}</p>
          <p><span className="text-muted-foreground">Created:</span> {new Date(worker.created_at).toLocaleString()}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Actions</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button onClick={() => updateStatus("active")} disabled={updating || worker.status === "active"}>Set Active</Button>
          <Button onClick={() => updateStatus("idle")} disabled={updating || worker.status === "idle"}>Set Idle</Button>
          <Button onClick={() => updateStatus("maintenance")} disabled={updating || worker.status === "maintenance"}>Set Maintenance</Button>
          <Button onClick={() => updateStatus("offline")} disabled={updating || worker.status === "offline"}>Set Offline</Button>
        </CardContent>
      </Card>
    </div>
  )
}
