"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Search, Plus, Save, X, History, RotateCcw } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"

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

interface PromptVersion {
  id: string
  version: number
  status: string
  name: string
  description: string | null
  category: string | null
  text: string
  variables: string[]
  compatible_models: string[]
  created_at: string
  published_at: string | null
}

interface DiffLine {
  type: "added" | "removed" | "unchanged"
  content: string
}

function computeDiff(oldText: string, newText: string): DiffLine[] {
  const oldLines = oldText.split("\n")
  const newLines = newText.split("\n")
  const result: DiffLine[] = []
  let i = 0
  let j = 0
  while (i < oldLines.length || j < newLines.length) {
    if (i >= oldLines.length) {
      result.push({ type: "added", content: newLines[j] })
      j++
    } else if (j >= newLines.length) {
      result.push({ type: "removed", content: oldLines[i] })
      i++
    } else if (oldLines[i] === newLines[j]) {
      result.push({ type: "unchanged", content: oldLines[i] })
      i++
      j++
    } else if (newLines.includes(oldLines[i], j)) {
      result.push({ type: "added", content: newLines[j] })
      j++
    } else {
      result.push({ type: "removed", content: oldLines[i] })
      i++
    }
  }
  return result
}

export function AdminPrompts() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [search, setSearch] = useState("")
  const [editing, setEditing] = useState<PromptTemplate | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [draft, setDraft] = useState<Partial<PromptTemplate>>({})
  const [saving, setSaving] = useState(false)
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [loadingVersions, setLoadingVersions] = useState(false)
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null)
  const [diffFrom, setDiffFrom] = useState<PromptVersion | null>(null)
  const [diffTo, setDiffTo] = useState<PromptVersion | null>(null)
  const [diffOpen, setDiffOpen] = useState(false)
  const [rollbackVersion, setRollbackVersion] = useState<PromptVersion | null>(null)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const { items: prompts, loading, page, pageSize, total, setPage, setPageSize, setFilters, refetch } = useAdminList<PromptTemplate>({
    endpoint: "/admin/prompts",
    pageSize: 20,
    filters: search ? { search } : {},
    transform: (raw) => {
      const paginated = raw as { items: PromptTemplate[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(search ? { search } : {})
  }, [search, setFilters])

  const startEdit = (prompt: PromptTemplate | null) => {
    setEditing(prompt)
    setIsCreating(prompt === null)
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
      setIsCreating(false)
      setDraft({})
      toast({ title: t("notification.success") || "Success", description: editing ? "Prompt updated" : "Prompt created", variant: "success" })
      refetch()
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Save failed"
      toast({ title: t("notification.error") || "Error", description: message, variant: "error" })
    } finally {
      setSaving(false)
    }
  }

  const loadVersions = async (promptId: string) => {
    setLoadingVersions(true)
    try {
      const data = await apiFetch<PromptVersion[]>(`/admin/prompts/${promptId}/versions`)
      setVersions(data)
      setSelectedPromptId(promptId)
    } catch {
      setVersions([])
    } finally {
      setLoadingVersions(false)
    }
  }

  const openDiff = (v: PromptVersion) => {
    if (versions.length === 0) return
    const idx = versions.findIndex((vv) => vv.id === v.id)
    if (idx === -1) return
    if (idx === versions.length - 1) {
      toast({ title: "Info", description: "This is the latest version, no previous version to compare", variant: "default" })
      return
    }
    setDiffFrom(versions[idx + 1])
    setDiffTo(v)
    setDiffOpen(true)
  }

  const doRollback = async () => {
    if (!rollbackVersion) return
    try {
      await apiFetch(`/admin/prompts/${rollbackVersion.prompt_id}/rollback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: rollbackVersion.version }),
      })
      toast({ title: "Success", description: `Rolled back to version ${rollbackVersion.version}`, variant: "success" })
      setRollbackVersion(null)
      refetch()
      if (selectedPromptId) loadVersions(selectedPromptId)
    } catch (e: unknown) {
      toast({ title: "Error", description: (e as Error)?.message || "Rollback failed", variant: "error" })
    }
  }

  const diffLines = useMemo(() => {
    if (!diffFrom || !diffTo) return []
    return computeDiff(diffFrom.text, diffTo.text)
  }, [diffFrom, diffTo])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading prompts...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.prompts")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.prompts")}</p>
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

      {(editing !== null || isCreating) && (
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
              <Button variant="ghost" onClick={() => { setEditing(null); setIsCreating(false); setDraft({}) }}>
                <X className="h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Prompts ({total})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
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
                      <div className="flex justify-end gap-1">
                        <Button size="sm" variant="ghost" aria-label={`View versions for ${prompt.code}`} onClick={() => loadVersions(prompt.id)}>
                          <History className="h-4 w-4" aria-hidden="true" />
                        </Button>
                        <Button size="sm" variant="ghost" aria-label={`Edit prompt ${prompt.code}`} onClick={() => startEdit(prompt)}>Edit</Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {prompts.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-muted-foreground">No prompts found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
        </CardContent>
      </Card>

      {selectedPromptId && (
        <Card>
          <CardHeader>
            <CardTitle>Version History</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingVersions ? (
              <p className="text-sm text-muted-foreground">Loading versions...</p>
            ) : versions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No versions found</p>
            ) : (
              <div className="space-y-2">
                {versions.map((v) => (
                  <div key={v.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <div className="font-medium">Version {v.version}</div>
                      <div className="text-xs text-muted-foreground">
                        {v.created_at ? new Date(v.created_at).toLocaleString() : "—"}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={v.status === "published" ? "default" : "secondary"}>{v.status}</Badge>
                      <Button size="sm" variant="ghost" onClick={() => openDiff(v)} aria-label={`Diff version ${v.version}`}>Diff</Button>
                      <Button size="sm" variant="ghost" onClick={() => setRollbackVersion(v)} aria-label={`Rollback to version ${v.version}`}>
                        <RotateCcw className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Dialog open={diffOpen} onOpenChange={setDiffOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Diff: v{diffFrom?.version} → v{diffTo?.version}</DialogTitle>
            <DialogDescription>Compare text changes between versions</DialogDescription>
          </DialogHeader>
          <div className="overflow-auto max-h-[60vh] rounded border bg-muted/30 p-2 font-mono text-xs">
            {diffLines.map((line, idx) => (
              <div
                key={idx}
                className={`px-2 py-0.5 ${
                  line.type === "added" ? "bg-green-100 text-green-900" :
                  line.type === "removed" ? "bg-red-100 text-red-900 line-through" :
                  "text-muted-foreground"
                }`}
              >
                {line.type === "added" ? "+ " : line.type === "removed" ? "- " : "  "}
                {line.content || "\u00A0"}
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!rollbackVersion} onOpenChange={(open) => !open && setRollbackVersion(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rollback to version {rollbackVersion?.version}?</DialogTitle>
            <DialogDescription>
              This will create a new version with the content of version {rollbackVersion?.version}.
              The current version will not be lost, but a new version will be added to the history.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setRollbackVersion(null)}>Cancel</Button>
            <Button onClick={doRollback}>Confirm Rollback</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
