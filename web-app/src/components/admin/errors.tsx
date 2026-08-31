"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface ErrorEntry {
  id: string
  error_code: string | null
  error_message: string | null
  model_name: string | null
  project_id: string
  attempt: number
  cost_rub: number
  duration_ms: number | null
  created_at: string
  resolved: boolean
}

interface ErrorsResponse {
  groups: Record<string, ErrorEntry[]>
  total: number
  occurrences: Record<string, number>
}

const ERROR_GROUPS = ["cuda", "api", "timeout", "storage", "payment", "validation", "moderation", "worker", "database", "other"]

const GROUP_LABELS: Record<string, string> = {
  cuda: "CUDA Errors",
  api: "API Errors",
  timeout: "Timeout Errors",
  storage: "Storage Errors",
  payment: "Payment Errors",
  validation: "Validation Errors",
  moderation: "Moderation Errors",
  worker: "Worker Errors",
  database: "Database Errors",
  other: "Other Errors",
}

export function AdminErrors() {
  const [errorsData, setErrorsData] = useState<ErrorsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadErrors = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<ErrorsResponse>("/admin/errors")
      setErrorsData(data)
    } catch {
      setErrorsData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadErrors()
  }, [user])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading errors...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Error Center</h1><p className="text-muted-foreground mt-1">Grouped generation errors</p></div>

      {errorsData && (
        <>
          <Card>
            <CardHeader><CardTitle>Error Statistics</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {ERROR_GROUPS.map((group) => {
                  const count = errorsData.occurrences[group] || 0
                  if (count === 0) return null
                  return (
                    <div key={group} className="border rounded-lg p-3 text-center cursor-pointer hover:bg-accent" onClick={() => setSelectedGroup(selectedGroup === group ? null : group)}>
                      <Badge className="mb-1">{GROUP_LABELS[group] || group}</Badge>
                      <p className="font-bold text-lg">{count}</p>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {selectedGroup && errorsData.groups[selectedGroup] && (
            <Card>
              <CardHeader><CardTitle>{GROUP_LABELS[selectedGroup] || selectedGroup}</CardTitle></CardHeader>
              <CardContent>
                <table className="w-full text-sm">
                  <thead><tr className="border-b"><th className="text-left py-2">Error ID</th><th className="text-left py-2">Code</th><th className="text-left py-2">Message</th><th className="text-left py-2">Model</th><th className="text-left py-2">Created</th></tr></thead>
                  <tbody>
                    {errorsData.groups[selectedGroup].map((err) => (
                      <tr key={err.id} className="border-b">
                        <td className="py-2 font-mono">{err.id.slice(0, 8)}…</td>
                        <td className="py-2">{err.error_code || "—"}</td>
                        <td className="py-2 max-w-xs truncate">{err.error_message || "—"}</td>
                        <td className="py-2">{err.model_name || "—"}</td>
                        <td className="py-2">{new Date(err.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
