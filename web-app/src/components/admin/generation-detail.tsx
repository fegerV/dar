"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface GenerationStep {
  id: string
  step_no: number
  step_code: string
  type: string
  status: string
  cost_rub: number
  duration_ms: number | null
  started_at: string | null
  completed_at: string | null
  error_code: string | null
  error_message: string | null
}

interface GenerationDetail {
  id: string
  project_id: string
  parent_generation_id: string | null
  template_version_id: string | null
  type: string
  status: string
  attempt: number
  requested_by_user_id: string | null
  provider_id: string | null
  model_name: string | null
  input_json: Record<string, unknown>
  output_json: Record<string, unknown>
  error_code: string | null
  error_message: string | null
  cost_rub: number
  duration_ms: number | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  progress: number
  current_step: string | null
  estimated_seconds: number | null
  steps: GenerationStep[]
}

const STATUS_COLORS: Record<string, string> = {
  SUCCESS: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
  RUNNING: "bg-blue-100 text-blue-800",
  PENDING: "bg-yellow-100 text-yellow-800",
  COMPLETED: "bg-green-100 text-green-800",
  CANCELED: "bg-gray-100 text-gray-800",
}

export function AdminGenerationDetail() {
  const [gen, setGen] = useState<GenerationDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadGen = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<GenerationDetail>(`/admin/generations/${params.id}`)
      setGen(data)
    } catch (e: unknown) {
      alert((e as Error)?.message || "Failed to load generation")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user && params.id) loadGen()
  }, [user, params.id])

  const handleRetry = async () => {
    if (!confirm("Retry this generation?")) return
    try {
      await apiFetch(`/admin/generations/${params.id}/retry`, { method: "POST" })
      alert("Retry initiated")
      loadGen()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Retry failed")
    }
  }

  const handleCancel = async () => {
    if (!confirm("Cancel this generation?")) return
    try {
      await apiFetch(`/admin/generations/${params.id}/cancel`, { method: "POST" })
      await loadGen()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Cancel failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading generation...</p>
  }

  if (!gen) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Generation #{gen.id.slice(0, 8)}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge className={STATUS_COLORS[gen.status] || "bg-gray-100"}>{gen.status}</Badge>
            <span className="text-sm text-muted-foreground">Attempt {gen.attempt}</span>
          </div>
        </div>
        <div className="flex gap-2">
          {gen.status !== "completed" && gen.status !== "canceled" && (
            <>
              <Button variant="outline" onClick={handleRetry}>Retry</Button>
              <Button variant="destructive" onClick={handleCancel}>Cancel</Button>
            </>
          )}
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Generation Info</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><p className="text-muted-foreground">Model</p><p className="font-medium">{gen.model_name || "—"}</p></div>
            <div><p className="text-muted-foreground">Project</p><p className="font-mono">{gen.project_id.slice(0, 8)}…</p></div>
            <div><p className="text-muted-foreground">Cost</p><p className="font-medium">{gen.cost_rub} ₽</p></div>
            <div><p className="text-muted-foreground">Duration</p><p className="font-medium">{gen.duration_ms ? `${gen.duration_ms / 1000}s` : "—"}</p></div>
          </div>
          {gen.error_message && <p className="mt-2 text-sm text-red-600">{gen.error_message}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Input</CardTitle></CardHeader>
        <CardContent>
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto">{JSON.stringify(gen.input_json, null, 2)}</pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Output</CardTitle></CardHeader>
        <CardContent>
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto">{JSON.stringify(gen.output_json, null, 2)}</pre>
        </CardContent>
      </Card>

      {gen.steps && gen.steps.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Steps ({gen.steps.length})</CardTitle></CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead><tr className="border-b"><th className="text-left py-2">#</th><th className="text-left py-2">Code</th><th className="text-left py-2">Status</th><th className="text-left py-2">Duration</th><th className="text-left py-2">Cost</th><th className="text-left py-2">Error</th></tr></thead>
              <tbody>
                {gen.steps.map((step) => (
                  <tr key={step.id} className="border-b">
                    <td className="py-2">{step.step_no}</td>
                    <td className="py-2">{step.step_code}</td>
                    <td className="py-2"><Badge variant="secondary">{step.status}</Badge></td>
                    <td className="py-2">{step.duration_ms ? `${step.duration_ms / 1000}s` : "—"}</td>
                    <td className="py-2">{step.cost_rub} ₽</td>
                    <td className="py-2">{step.error_message || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
