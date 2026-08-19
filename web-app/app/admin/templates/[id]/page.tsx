"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface TemplateDetail {
  id: string
  code: string
  title: string
  description?: string
  kind: string
  status: string
  category?: string
  base_price_rub: number
  created_at: string
}

interface TemplateVersion {
  id: string
  version: number
  status: string
  prompt_config: Record<string, unknown>
  created_at: string
  published_at?: string
}

interface Scene {
  id: string
  code: string
  title: string
  duration_sec?: number
  status?: string
}

export default function AdminTemplateDetailPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [template, setTemplate] = useState<TemplateDetail | null>(null)
  const [versions, setVersions] = useState<TemplateVersion[]>([])
  const [scenes, setScenes] = useState<Scene[]>([])
  const [loading, setLoading] = useState(true)
  const [editStatus, setEditStatus] = useState("")

  const templateId = params.id

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const loadTemplate = async () => {
    setLoading(true)
    try {
      const [t, v, s] = await Promise.all([
        apiFetch<TemplateDetail>(`/admin/templates/${templateId}`),
        apiFetch<TemplateVersion[]>(`/admin/templates/${templateId}/versions`).catch(() => []),
        apiFetch<Scene[]>(`/admin/templates/${templateId}/scenes`).catch(() => []),
      ])
      setTemplate(t)
      setVersions(v)
      setScenes(s)
      setEditStatus(t.status)
    } catch {
      // stay on page
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user && templateId) loadTemplate()
  }, [user, templateId])

  const saveStatus = async () => {
    if (!template) return
    try {
      await apiFetch<TemplateDetail>(`/admin/templates/${template.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: editStatus }),
      })
      const updated = await apiFetch<TemplateDetail>(`/admin/templates/${template.id}`)
      setTemplate(updated)
      alert("Template updated")
    } catch (e: unknown) {
      alert((e as Error)?.message || "Update failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading template...</p>
  }

  if (!template) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{template.title}</h1>
          <p className="text-sm text-muted-foreground code">{template.code}</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Template Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Status</label>
            <div className="flex gap-2 mt-1">
              <Input value={editStatus} onChange={(e) => setEditStatus(e.target.value)} />
              <Button onClick={saveStatus}>Save</Button>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Base Price</label>
            <p className="text-sm">{template.base_price_rub} RUB</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Versions ({versions.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {versions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No versions</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Version</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-left py-2">Created</th>
                </tr>
              </thead>
              <tbody>
                {versions.map((v) => (
                  <tr key={v.id} className="border-b">
                    <td className="py-2">{v.version}</td>
                    <td className="py-2">
                      <Badge>{v.status}</Badge>
                    </td>
                    <td className="py-2">{new Date(v.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Scenes ({scenes.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {scenes.length === 0 ? (
            <p className="text-sm text-muted-foreground">No scenes</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Code</th>
                  <th className="text-left py-2">Title</th>
                  <th className="text-left py-2">Duration</th>
                </tr>
              </thead>
              <tbody>
                {scenes.map((s) => (
                  <tr key={s.id} className="border-b">
                    <td className="py-2 font-mono">{s.code}</td>
                    <td className="py-2">{s.title}</td>
                    <td className="py-2">{s.duration_sec ? `${s.duration_sec}s` : "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
