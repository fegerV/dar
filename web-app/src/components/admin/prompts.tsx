"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Search, Plus, Save, X } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface PromptTemplate {
  id: string
  code: string
  name: string
  description: string | null
  category: string | null
  text: string
  variables: string[]
  compatible_models: string[]
  is_active: boolean
  version: number
  success_rate: number | null
  usage_count: number
  rating: number | null
  created_at: string
  updated_at: string | null
}

export function AdminPrompts() {
  const [prompts, setPrompts] = useState<PromptTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [editing, setEditing] = useState<PromptTemplate | null>(null)
  const [draft, setDraft] = useState<Partial<PromptTemplate>>({})
  const [saving, setSaving] = useState(false)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadPrompts = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (search) params.set("search", search)
      const data = await apiFetch<PromptTemplate[]>(`/admin/prompts?${params.toString()}`)
      setPrompts(data)
    } catch {
      setPrompts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadPrompts()
  }, [user, search])

  const startEdit = (prompt: PromptTemplate | null) => {
    setEditing(prompt)
    setDraft(prompt || { code: "", name: "", text: "", variables: [], compatible_models: [], is_active: true, category: "", description: "" })
  }

  const savePrompt = async () => {
    setSaving(true)
    try {
      if (editing) {
        await apiFetch<PromptTemplate>(`/admin/prompts/${editing.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(draft),
        })
      } else {
        await apiFetch<PromptTemplate>("/admin/prompts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code: draft.code,
            name: draft.name,
            description: draft.description,
            category: draft.category,
            text: draft.text,
            variables: draft.variables,
            compatible_models: draft.compatible_models,
            is_active: draft.is_active,
          }),
        })
      }
      setEditing(null)
      setDraft({})
      loadPrompts()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Save failed")
    } finally {
      setSaving(false)
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading prompts...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Prompt Library</h1>
          <p className="text-muted-foreground mt-1">Manage prompt templates with versioning</p>
        </div>
        <Button onClick={() => startEdit(null)}>
          <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
          New Prompt
        </Button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
        <Input
          placeholder="Search prompts..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-9"
          aria-label="Search prompts"
        />
      </div>

      {editing !== null && (
        <Card>
          <CardHeader>
            <CardTitle>{editing ? "Edit Prompt" : "New Prompt"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Code</Label><Input value={draft.code || ""} onChange={e => setDraft({ ...draft, code: e.target.value })} aria-label="Code" /></div>
              <div><Label>Name</Label><Input value={draft.name || ""} onChange={e => setDraft({ ...draft, name: e.target.value })} aria-label="Name" /></div>
            </div>
            <div><Label>Description</Label><Textarea value={draft.description || ""} onChange={e => setDraft({ ...draft, description: e.target.value })} aria-label="Description" /></div>
            <div><Label>Category</Label><Input value={draft.category || ""} onChange={e => setDraft({ ...draft, category: e.target.value })} aria-label="Category" /></div>
            <div><Label>Text (use {'{'}variable{'}'} placeholders)</Label><Textarea value={draft.text || ""} onChange={e => setDraft({ ...draft, text: e.target.value })} rows={6} aria-label="Prompt text" /></div>
            <div>
              <Label>Variables (comma-separated)</Label>
              <Input
                value={(draft.variables || []).join(", ")}
                onChange={e => setDraft({ ...draft, variables: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
                aria-label="Variables"
              />
            </div>
            <div>
              <Label>Compatible Models (comma-separated)</Label>
              <Input
                value={(draft.compatible_models || []).join(", ")}
                onChange={e => setDraft({ ...draft, compatible_models: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
                aria-label="Compatible models"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={savePrompt} disabled={saving}>{saving ? "Saving..." : <><Save className="h-4 w-4 mr-2" aria-hidden="true" />Save</>}</Button>
              <Button variant="ghost" onClick={() => { setEditing(null); setDraft({}) }}>
                <X className="h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Prompts ({prompts.length})</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Code</th><th className="text-left py-2">Name</th><th className="text-left py-2">Category</th><th className="text-left py-2">Vars</th><th className="text-center py-2">Active</th><th className="text-center py-2">Version</th><th className="text-right py-2">Usage</th><th className="text-right py-2">Actions</th></tr></thead>
            <tbody>
              {prompts.map((prompt) => (
                <tr key={prompt.id} className="border-b">
                  <td className="py-2 font-mono">{prompt.code}</td>
                  <td className="py-2">{prompt.name}</td>
                  <td className="py-2">{prompt.category || "—"}</td>
                  <td className="py-2">{(prompt.variables || []).join(", ") || "—"}</td>
                  <td className="py-2 text-center">
                    <Badge variant={prompt.is_active ? "default" : "secondary"}>{prompt.is_active ? "Yes" : "No"}</Badge>
                  </td>
                  <td className="py-2 text-center">{prompt.version}</td>
                  <td className="py-2 text-right">{prompt.usage_count}</td>
                  <td className="py-2 text-right">
                    <Button size="sm" variant="ghost" aria-label={`Edit prompt ${prompt.code}`} onClick={() => startEdit(prompt)}>Edit</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
