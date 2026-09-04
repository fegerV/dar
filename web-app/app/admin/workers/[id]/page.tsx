"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useToast } from "@/components/ui/toast"
import type { AdminWorkerDetailResponse } from "@/types/admin"

interface WorkerLog {
  id: string
  level: string
  message: string
  created_at: string
}

export default function AdminWorkerDetailPage() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [worker, setWorker] = useState<AdminWorkerDetailResponse | null>(null)
  const [logs, setLogs] = useState<WorkerLog[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [workerParams, setWorkerParams] = useState({ gpu_model: "", gpu_vram_total_gb: "", cpu_usage_percent: "" })
  const [savingParams, setSavingParams] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadWorker = useCallback(async () => {
    if (!user || !params.id) return
    setLoading(true)
    try {
      const [w, l] = await Promise.all([
        apiFetch<AdminWorkerDetailResponse>(`/admin/workers/${params.id}`),
        apiFetch<WorkerLog[]>(`/admin/workers/${params.id}/logs`).catch(() => []),
      ])
      setWorker(w)
      setLogs(l)
      setWorkerParams({
        gpu_model: w.gpu_model || "",
        gpu_vram_total_gb: w.gpu_vram_total_gb?.toString() || "",
        cpu_usage_percent: w.cpu_usage_percent?.toString() || "",
      })
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
      toast({ title: "Success", description: `Worker status: ${status}`, variant: "success" })
      await loadWorker()
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Status update failed", variant: "error" })
    } finally {
      setUpdating(false)
    }
  }

  const saveParams = async () => {
    if (!worker) return
    setSavingParams(true)
    try {
      await apiFetch(`/admin/workers/${worker.id}/params`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gpu_model: workerParams.gpu_model || null,
          gpu_vram_total_gb: workerParams.gpu_vram_total_gb ? parseInt(workerParams.gpu_vram_total_gb) : null,
          cpu_usage_percent: workerParams.cpu_usage_percent ? parseFloat(workerParams.cpu_usage_percent) : null,
        }),
      })
      toast({ title: "Success", description: "Parameters updated", variant: "success" })
      await loadWorker()
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Save failed", variant: "error" })
    } finally {
      setSavingParams(false)
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
        <CardHeader><CardTitle>Status</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button onClick={() => updateStatus("active")} disabled={updating || worker.status === "active"}>Set Active</Button>
          <Button onClick={() => updateStatus("idle")} disabled={updating || worker.status === "idle"}>Set Idle</Button>
          <Button onClick={() => updateStatus("maintenance")} disabled={updating || worker.status === "maintenance"}>Set Maintenance</Button>
          <Button onClick={() => updateStatus("offline")} disabled={updating || worker.status === "offline"}>Set Offline</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Parameters</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label>GPU Model</Label>
              <Input value={workerParams.gpu_model} onChange={(e) => setWorkerParams({ ...workerParams, gpu_model: e.target.value })} />
            </div>
            <div>
              <Label>VRAM Total (GB)</Label>
              <Input type="number" value={workerParams.gpu_vram_total_gb} onChange={(e) => setWorkerParams({ ...workerParams, gpu_vram_total_gb: e.target.value })} />
            </div>
            <div>
              <Label>CPU Usage (%)</Label>
              <Input type="number" step="0.1" value={workerParams.cpu_usage_percent} onChange={(e) => setWorkerParams({ ...workerParams, cpu_usage_percent: e.target.value })} />
            </div>
          </div>
          <Button onClick={saveParams} disabled={savingParams}>{savingParams ? "Saving..." : "Save Parameters"}</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Logs ({logs.length})</CardTitle></CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No logs</p>
          ) : (
            <div className="space-y-1 max-h-96 overflow-y-auto rounded border bg-muted/30 p-2 font-mono text-xs">
              {logs.map((log) => (
                <div key={log.id} className="flex gap-2">
                  <span className="text-muted-foreground">{new Date(log.created_at).toLocaleTimeString()}</span>
                  <Badge variant={log.level === "error" ? "destructive" : log.level === "warning" ? "secondary" : "outline"} className="text-xs">{log.level}</Badge>
                  <span>{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
