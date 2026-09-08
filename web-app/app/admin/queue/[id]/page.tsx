"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import type { AdminQueueJob } from "@/types/admin"

interface WorkerInfo {
  id: string
  name: string
}

export default function AdminQueueJobDetailPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [job, setJob] = useState<AdminQueueJob | null>(null)
  const [worker, setWorker] = useState<WorkerInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (user && params.id) {
      setLoading(true)
      Promise.all([
        apiFetch<AdminQueueJob>(`/admin/queue/jobs/${params.id}`),
        apiFetch<WorkerInfo[]>(`/admin/workers`).catch(() => []),
      ])
        .then(([jobData, workers]) => {
          setJob(jobData)
          const w = workers.find((wk) => wk.id === jobData.worker_id)
          setWorker(w || null)
        })
        .catch(() => setJob(null))
        .finally(() => setLoading(false))
    }
  }, [user, params.id])

  const retryJob = async () => {
    if (!job) return
    try {
      await apiFetch(`/admin/queue/${job.id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "retry" }),
      })
      alert("Job retried successfully")
      router.refresh()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Retry failed")
    }
  }

  const cancelJob = async () => {
    if (!job) return
    if (!confirm("Cancel this job?")) return
    try {
      await apiFetch(`/admin/queue/${job.id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "cancel" }),
      })
      alert("Job canceled")
      router.back()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Cancel failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading job details...</p>
  }

  if (!job) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.queue")}</h1>
          <p className="text-muted-foreground mt-1">Job {job.id?.slice(0, 8)}…</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Job Details</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p><span className="text-muted-foreground">ID:</span> <span className="font-mono">{job.id}</span></p>
          <p><span className="text-muted-foreground">Generation ID:</span> <span className="font-mono">{job.generation_id || "—"}</span></p>
          <p><span className="text-muted-foreground">Status:</span> <Badge>{job.status}</Badge></p>
          <p><span className="text-muted-foreground">Priority:</span> {job.priority}</p>
          <p><span className="text-muted-foreground">Retry Count:</span> {job.retry_count}</p>
          <p><span className="text-muted-foreground">Error Code:</span> {job.error_code || "—"}</p>
          <p><span className="text-muted-foreground">Error Message:</span> {job.error_message || "—"}</p>
          <p><span className="text-muted-foreground">Worker:</span> {worker ? `${worker.name} (${worker.id.slice(0, 8)}…)` : job.worker_id ? job.worker_id.slice(0, 8) + "…" : "—"}</p>
          <p><span className="text-muted-foreground">Started:</span> {job.started_at ? new Date(job.started_at).toLocaleString() : "—"}</p>
          <p><span className="text-muted-foreground">Finished:</span> {job.finished_at ? new Date(job.finished_at).toLocaleString() : "—"}</p>
          <p><span className="text-muted-foreground">Created:</span> {job.created_at ? new Date(job.created_at).toLocaleString() : "—"}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Actions</CardTitle></CardHeader>
        <CardContent className="flex gap-2">
          {(job.status === "failed" || job.status === "canceled") && (
            <Button onClick={retryJob}>Retry Job</Button>
          )}
          {(job.status === "pending" || job.status === "queued" || job.status === "running") && (
            <Button variant="destructive" onClick={cancelJob}>Cancel Job</Button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
