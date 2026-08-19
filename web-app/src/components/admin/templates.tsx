"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Search, Plus, Edit } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminTemplate, AdminTemplateCreate } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

export function AdminTemplates() {
  const [search, setSearch] = useState("")
  const [templates, setTemplates] = useState<AdminTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<AdminTemplate[]>("/admin/templates")
      setTemplates(data)
    } catch {
      setTemplates([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadTemplates()
  }, [user])

  const filtered = templates.filter((tmpl) => {
    if (search && !tmpl.title.toLowerCase().includes(search.toLowerCase()) && !tmpl.code.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const [form, setForm] = useState<Partial<AdminTemplateCreate>>({
    code: "",
    title: "",
    kind: "video",
    base_price_rub: 590,
  })
  const [formError, setFormError] = useState("")

  const handleCreate = async () => {
    setFormError("")
    if (!form.code || !form.title) {
      setFormError("Code and title are required")
      return
    }
    try {
      await apiFetch<AdminTemplate>("/admin/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      setCreating(false)
      setForm({ code: "", title: "", kind: "video", base_price_rub: 590 })
      loadTemplates()
    } catch (err: unknown) {
      setFormError((err as Error)?.message || "Failed to create template")
    }
  }

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground mt-1">Manage template library and scenes</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading templates...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground mt-1">Manage template library and scenes</p>
        </div>
        <Button onClick={() => setCreating(!creating)} aria-label="Create new template" variant={creating ? "secondary" : "default"}>
          {creating ? "Cancel" : (
            <>
              <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
              New Template
            </>
          )}
        </Button>
      </div>

      {creating && (
        <Card>
          <CardHeader>
            <CardTitle>Create Template</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="code">Code</Label>
              <Input
                id="code"
                value={form.code || ""}
                onChange={(e) => setForm({ ...form, code: e.target.value })}
                aria-label="Template code"
              />
            </div>
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={form.title || ""}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                aria-label="Template title"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={form.description || ""}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                aria-label="Template description"
              />
            </div>
            <div>
              <Label htmlFor="base_price_rub">Base Price (RUB)</Label>
              <Input
                id="base_price_rub"
                type="number"
                value={form.base_price_rub || 590}
                onChange={(e) => setForm({ ...form, base_price_rub: parseInt(e.target.value) })}
                aria-label="Base price"
              />
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <Button onClick={handleCreate} className="w-full">Create Template</Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Search templates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              aria-label="Search templates"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Templates table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Code</th>
                  <th className="text-left py-3 px-4 font-medium">Title</th>
                  <th className="text-left py-3 px-4 font-medium">Category</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-right py-3 px-4 font-medium">Price</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tmpl) => (
                  <tr key={tmpl.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">{tmpl.code}</td>
                    <td className="py-3 px-4">{tmpl.title}</td>
                    <td className="py-3 px-4">{tmpl.category || "N/A"}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={tmpl.status === "published" || tmpl.status === "active" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                        {tmpl.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right">{tmpl.base_price_rub} RUB</td>
                     <td className="py-3 px-4 text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        aria-label={`Edit template ${tmpl.id}`}
                        onClick={() => router.push(`/admin/templates/${tmpl.id}`)}
                      >
                        <Edit className="h-4 w-4" aria-hidden="true" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        aria-label={`Delete template ${tmpl.id}`}
                        onClick={async () => {
                          if (!confirm(`Delete template ${tmpl.code}?`)) return
                          try {
                            await apiFetch(`/admin/templates/${tmpl.id}`, { method: "DELETE" })
                            loadTemplates()
                          } catch (e: unknown) {
                            alert((e as Error)?.message || "Delete failed")
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
