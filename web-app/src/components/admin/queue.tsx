"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { X, RotateCcw, Trash2 } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminQueueJob } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"

export function AdminQueue() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set())
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const { items: jobs, loading, page, pageSize, total, totalPages, setPage, setPageSize, setFilters, refetch } = useAdminList<AdminQueueJob>({
    endpoint: "/admin/queue",
    pageSize: 20,
    filters: statusFilter ? { status: statusFilter } : {},
    transform: (raw) => {
      const paginated = raw as { items: AdminQueueJob[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(statusFilter ? { status: statusFilter } : {})
  }, [statusFilter, setFilters])

  const runningJobs = jobs.filter((j) => j.status === "running")
  const pendingJobs = jobs.filter((j) => j.status === "pending" || j.status === "queued")

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.queue")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.queue")}</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading queue...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.sidebar.queue")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.pages.queue")}</p>
      </div>

      <Select value={statusFilter || ""} onValueChange={(v) => setStatusFilter(v || null)} className="w-[180px]" aria-label="Filter by status">
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="running">Running</option>
        <option value="failed">Failed</option>
        <option value="canceled">Canceled</option>
      </Select>

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
                  <span className="text-sm text-muted-foreground">Gen: {job.generation_id?.slice(0, 8)}…</span>
                </div>
                <div className="mb-2">
                  <Progress value={(job.retry_count + 1) * 25} aria-label={`Job ${job.id} progress`} />
                  <div className="text-xs text-muted-foreground mt-1">Retries: {job.retry_count}</div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    aria-label={`Cancel job ${job.id}`}
                    onClick={async () => {
                      try {
                        await apiFetch(`/admin/queue/${job.id}/action`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ action: "cancel" }),
                        })
                        toast({
                          title: t("notification.success") || "Success",
                          description: `Job ${job.id.slice(0, 8)} canceled`,
                          variant: "success",
                        })
                        refetch()
                      } catch {
                        // error handled by API
                      }
                    }}
                  >
                    <X className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </div>
              </div>
            ))}
            {runningJobs.length === 0 && (
              <p className="text-sm text-muted-foreground text-center">No running jobs</p>
            )}
          </CardContent>
        </Card>

         <Card>
          <CardHeader>
            <CardTitle>Pending</CardTitle>
            {selectedJobs.size > 0 && (
              <div className="flex gap-2 mt-2">
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={async () => {
                    if (!confirm(`Cancel ${selectedJobs.size} selected jobs?`)) return
                    try {
                      await apiFetch("/admin/queue/bulk-action", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ action: "cancel", job_ids: Array.from(selectedJobs) }),
                      })
                      setSelectedJobs(new Set())
                      toast({
                        title: t("notification.success") || "Success",
                        description: `${selectedJobs.size} jobs canceled`,
                        variant: "success",
                      })
                      refetch()
                    } catch (e: unknown) {
                      const message = e instanceof Error ? e.message : "Bulk cancel failed"
                      toast({
                        title: t("notification.error") || "Error",
                        description: message,
                        variant: "error",
                      })
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-1" aria-hidden="true" />
                  Cancel Selected ({selectedJobs.size})
                </Button>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {pendingJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      checked={selectedJobs.has(job.id)}
                      onCheckedChange={(checked) => {
                        const newSet = new Set(selectedJobs)
                        if (checked) newSet.add(job.id)
                        else newSet.delete(job.id)
                        setSelectedJobs(newSet)
                      }}
                      aria-label={`Select job ${job.id}`}
                    />
                    <span className="font-mono font-medium">#{job.id}</span>
                    <span className="ml-3 text-sm text-muted-foreground">Gen: {job.generation_id?.slice(0, 8)}…</span>
                    <span className="text-xs text-muted-foreground">Priority: {job.priority}</span>
                  </div>
                  <div className="flex gap-1 items-center">
                    <Input
                      type="number"
                      min={0}
                      max={1000}
                      defaultValue={job.priority}
                      className="w-16 h-8 text-xs"
                      aria-label={`Set priority for job ${job.id}`}
                      onBlur={async (e) => {
                        const val = parseInt(e.target.value)
                        if (isNaN(val) || val < 0 || val > 1000) return
                        try {
                          await apiFetch<AdminQueueJob>(`/admin/queue/${job.id}/priority`, {
                            method: "PATCH",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ priority: val }),
                          })
                          refetch()
                        } catch (e: unknown) {
                          const message = e instanceof Error ? e.message : "Priority update failed"
                          toast({
                            title: t("notification.error") || "Error",
                            description: message,
                            variant: "error",
                          })
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      aria-label={`Retry job ${job.id}`}
                      onClick={async () => {
                        try {
                          await apiFetch(`/admin/queue/${job.id}/action`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ action: "retry" }),
                          })
                          toast({
                            title: t("notification.success") || "Success",
                            description: `Job ${job.id.slice(0, 8)} retried`,
                            variant: "success",
                          })
                          refetch()
                        } catch {
                          // error handled by API
                        }
                      }}
                    >
                      <RotateCcw className="h-4 w-4" aria-hidden="true" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      aria-label={`Cancel job ${job.id}`}
                      onClick={async () => {
                        try {
                          await apiFetch(`/admin/queue/${job.id}/action`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ action: "cancel" }),
                          })
                          toast({
                            title: t("notification.success") || "Success",
                            description: `Job ${job.id.slice(0, 8)} canceled`,
                            variant: "success",
                          })
                          refetch()
                        } catch {
                          // error handled by API
                        }
                      }}
                    >
                      <X className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              ))}
              {pendingJobs.length === 0 && (
                <p className="text-sm text-muted-foreground text-center">No pending jobs</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
    </div>
  )
}
