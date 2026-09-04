"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useToast } from "@/components/ui/toast"
import { Save, Plus, X, GripVertical, Edit } from "lucide-react"

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
  description?: string
  duration_sec?: number
  source_type?: string
  sort_order: number
  scene_config?: Record<string, unknown>
}

interface SceneForm {
  code: string
  title: string
  description: string
  duration_sec: string
  source_type: string
  source_reference: string
}

export default function AdminTemplateDetailPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const { toast } = useToast()
  const [template, setTemplate] = useState<TemplateDetail | null>(null)
  const [versions, setVersions] = useState<TemplateVersion[]>([])
  const [scenes, setScenes] = useState<Scene[]>([])
  const [loading, setLoading] = useState(true)
  const [editStatus, setEditStatus] = useState("")
  const [sceneDialog, setSceneDialog] = useState<Scene | "new" | null>(null)
  const [sceneForm, setSceneForm] = useState<SceneForm>({
    code: "",
    title: "",
    description: "",
    duration_sec: "",
    source_type: "",
    source_reference: "",
  })
  const [sceneSaving, setSceneSaving] = useState(false)
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)

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
      setScenes(s.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0)))
      setEditStatus(t.status)
    } catch {
      // stay on page
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user && templateId) loadTemplate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      toast({ title: "Success", description: "Template updated", variant: "success" })
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Update failed", variant: "error" })
    }
  }

  const openNewScene = () => {
    setSceneForm({ code: "", title: "", description: "", duration_sec: "", source_type: "", source_reference: "" })
    setSceneDialog("new")
  }

  const openEditScene = (scene: Scene) => {
    setSceneForm({
      code: scene.code,
      title: scene.title,
      description: scene.description || "",
      duration_sec: scene.duration_sec?.toString() || "",
      source_type: scene.source_type || "",
      source_reference: "",
    })
    setSceneDialog(scene)
  }

  const saveScene = async () => {
    setSceneSaving(true)
    try {
      const payload = {
        code: sceneForm.code,
        title: sceneForm.title,
        description: sceneForm.description || null,
        duration_sec: sceneForm.duration_sec ? parseInt(sceneForm.duration_sec) : null,
        source_type: sceneForm.source_type || null,
        source_reference: sceneForm.source_reference || null,
        scene_config: {},
      }
      if (sceneDialog === "new") {
        await apiFetch(`/admin/templates/${templateId}/scenes`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })
        toast({ title: "Success", description: "Scene created", variant: "success" })
      } else if (sceneDialog) {
        await apiFetch(`/admin/scenes/${sceneDialog.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: payload.title,
            description: payload.description,
            duration_sec: payload.duration_sec,
            source_type: payload.source_type,
            source_reference: payload.source_reference,
          }),
        })
        toast({ title: "Success", description: "Scene updated", variant: "success" })
      }
      setSceneDialog(null)
      await loadTemplate()
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Save failed", variant: "error" })
    } finally {
      setSceneSaving(false)
    }
  }

  const deleteScene = async (scene: Scene) => {
    if (!confirm(`Delete scene "${scene.title}"?`)) return
    try {
      await apiFetch(`/admin/scenes/${scene.id}`, { method: "DELETE" })
      toast({ title: "Success", description: "Scene deleted", variant: "success" })
      await loadTemplate()
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Delete failed", variant: "error" })
    }
  }

  const reorderScenes = async (newOrder: Scene[]) => {
    setScenes(newOrder)
    try {
      await apiFetch(`/admin/scenes/reorder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scene_ids: newOrder.map((s) => s.id) }),
      })
      toast({ title: "Success", description: "Scenes reordered", variant: "success" })
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Reorder failed", variant: "error" })
      await loadTemplate()
    }
  }

  const handleDragStart = (index: number) => {
    setDragIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    setDragOverIndex(index)
  }

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault()
    if (dragIndex === null || dragIndex === dropIndex) {
      setDragIndex(null)
      setDragOverIndex(null)
      return
    }
    const newOrder = [...scenes]
    const [movedItem] = newOrder.splice(dragIndex, 1)
    newOrder.splice(dropIndex, 0, movedItem)
    const withOrder = newOrder.map((s, idx) => ({ ...s, sort_order: idx }))
    reorderScenes(withOrder)
    setDragIndex(null)
    setDragOverIndex(null)
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
            <Label>Status</Label>
            <div className="flex gap-2 mt-1">
              <Input value={editStatus} onChange={(e) => setEditStatus(e.target.value)} />
              <Button onClick={saveStatus}><Save className="h-4 w-4 mr-2" />Save</Button>
            </div>
          </div>
          <div>
            <Label>Base Price</Label>
            <p className="text-sm">{template.base_price_rub} RUB</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Scenes ({scenes.length})</CardTitle>
            <Button size="sm" onClick={openNewScene}>
              <Plus className="h-4 w-4 mr-2" />Add Scene
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {scenes.length === 0 ? (
            <p className="text-sm text-muted-foreground">No scenes</p>
          ) : (
            <div className="space-y-2">
              {scenes.map((s, idx) => (
                <div
                  key={s.id}
                  draggable
                  onDragStart={() => handleDragStart(idx)}
                  onDragOver={(e) => handleDragOver(e, idx)}
                  onDrop={(e) => handleDrop(e, idx)}
                  onDragEnd={() => { setDragIndex(null); setDragOverIndex(null) }}
                  className={`flex items-center gap-3 rounded-lg border p-3 cursor-move transition-colors ${
                    dragIndex === idx ? "opacity-50" : ""
                  } ${dragOverIndex === idx && dragIndex !== idx ? "border-primary bg-primary/5" : ""}`}
                >
                  <GripVertical className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-muted-foreground">#{idx + 1}</span>
                      <span className="font-mono text-sm">{s.code}</span>
                      <span className="font-medium">{s.title}</span>
                      {s.duration_sec && <Badge variant="secondary">{s.duration_sec}s</Badge>}
                    </div>
                    {s.description && (
                      <p className="text-xs text-muted-foreground mt-1 truncate">{s.description}</p>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEditScene(s)}>
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => deleteScene(s)}>
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
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

      <Dialog open={!!sceneDialog} onOpenChange={(open) => !open && setSceneDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{sceneDialog === "new" ? "New Scene" : "Edit Scene"}</DialogTitle>
            <DialogDescription>
              {sceneDialog === "new" ? "Add a new scene to this template" : "Update scene details"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Code</Label>
                <Input value={sceneForm.code} onChange={(e) => setSceneForm({ ...sceneForm, code: e.target.value })} disabled={sceneDialog !== "new"} />
              </div>
              <div>
                <Label>Duration (sec)</Label>
                <Input type="number" value={sceneForm.duration_sec} onChange={(e) => setSceneForm({ ...sceneForm, duration_sec: e.target.value })} />
              </div>
            </div>
            <div>
              <Label>Title</Label>
              <Input value={sceneForm.title} onChange={(e) => setSceneForm({ ...sceneForm, title: e.target.value })} />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={sceneForm.description} onChange={(e) => setSceneForm({ ...sceneForm, description: e.target.value })} rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Source Type</Label>
                <Input value={sceneForm.source_type} onChange={(e) => setSceneForm({ ...sceneForm, source_type: e.target.value })} placeholder="library, original, custom" />
              </div>
              <div>
                <Label>Source Reference</Label>
                <Input value={sceneForm.source_reference} onChange={(e) => setSceneForm({ ...sceneForm, source_reference: e.target.value })} />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setSceneDialog(null)}>Cancel</Button>
              <Button onClick={saveScene} disabled={sceneSaving}>
                {sceneSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
