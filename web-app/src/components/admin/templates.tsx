"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Search, Plus, Edit, LayoutGrid, Table as TableIcon, Clock, Star, TrendingUp, Zap } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminTemplate, AdminTemplateCreate } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"

const CATEGORIES = [
  { key: "all", icon: "🎯" },
  { key: "birthday", icon: "🎂" },
  { key: "holiday", icon: "🎄" },
  { key: "cinematic", icon: "🎬" },
  { key: "humor", icon: "😂" },
  { key: "romantic", icon: "❤️" },
  { key: "family", icon: "👨‍👩‍👧" },
  { key: "corporate", icon: "💼" },
  { key: "wedding", icon: "💍" },
  { key: "emotional", icon: "🥹" },
  { key: "music", icon: "🎵" },
  { key: "thematic", icon: "🎭" },
]

export function AdminTemplates() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")
  const [category, setCategory] = useState("all")
  const [templates, setTemplates] = useState<AdminTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [viewMode, setViewMode] = useState<"catalog" | "table">("catalog")
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
    if (category !== "all" && tmpl.category !== category) return false
    return true
  })

  const [form, setForm] = useState<Partial<AdminTemplateCreate>>({
    code: "",
    title: "",
    kind: "video",
    base_price_rub: 590,
    cost_price_rub: 177,
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
      setForm({ code: "", title: "", kind: "video", base_price_rub: 590, cost_price_rub: 177 })
      loadTemplates()
    } catch (err: unknown) {
      setFormError((err as Error)?.message || "Failed to create template")
    }
  }

  const getDifficultyLabel = (d: number | null | undefined) => {
    if (!d) return "—"
    if (d <= 1) return "★☆☆☆☆"
    if (d <= 2) return "★★☆☆☆"
    if (d <= 3) return "★★★☆☆"
    if (d <= 4) return "★★★★☆"
    return "★★★★★"
  }

  const getCategoryIcon = (cat: string | null | undefined) => {
    const found = CATEGORIES.find((c) => c.key === cat)
    return found?.icon || "📦"
  }

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.templates")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.templates")}</p>
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
          <h1 className="text-3xl font-bold">{t("admin.sidebar.templates")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.templates")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={viewMode === "catalog" ? "default" : "outline"}
            onClick={() => setViewMode("catalog")}
            aria-label={t("admin.templates.catalog_view")}
          >
            <LayoutGrid className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            size="sm"
            variant={viewMode === "table" ? "default" : "outline"}
            onClick={() => setViewMode("table")}
            aria-label={t("admin.templates.table_view")}
          >
            <TableIcon className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button onClick={() => setCreating(!creating)} aria-label={t("admin.templates.create_template")} variant={creating ? "secondary" : "default"}>
            {creating ? "Cancel" : (
              <>
                <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
                {t("admin.templates.create_template")}
              </>
            )}
          </Button>
        </div>
      </div>

      {creating && (
        <Card>
          <CardHeader>
            <CardTitle>{t("admin.templates.create_template")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
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
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="base_price_rub">{t("admin.templates.price")} (RUB)</Label>
                <Input
                  id="base_price_rub"
                  type="number"
                  value={form.base_price_rub || 590}
                  onChange={(e) => setForm({ ...form, base_price_rub: parseInt(e.target.value) })}
                  aria-label="Base price"
                />
              </div>
              <div>
                <Label htmlFor="cost_price_rub">{t("admin.templates.cost_price")} (RUB)</Label>
                <Input
                  id="cost_price_rub"
                  type="number"
                  value={form.cost_price_rub || 177}
                  onChange={(e) => setForm({ ...form, cost_price_rub: parseInt(e.target.value) })}
                  aria-label="Cost price"
                />
              </div>
              <div>
                <Label htmlFor="category">{t("admin.templates.category")}</Label>
                <select
                  id="category"
                  value={form.category || ""}
                  onChange={(e) => setForm({ ...form, category: e.target.value || undefined })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <option value="">—</option>
                  {CATEGORIES.filter((c) => c.key !== "all").map((c) => (
                    <option key={c.key} value={c.key}>{c.icon} {t(`admin.templates.categories.${c.key}`)}</option>
                  ))}
                </select>
              </div>
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <Button onClick={handleCreate} className="w-full">{t("admin.templates.create_template")}</Button>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-wrap items-center gap-4">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Input
            placeholder={t("admin.templates.search_placeholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
            aria-label={t("admin.templates.search_placeholder")}
          />
        </div>
        <div className="flex flex-wrap gap-1">
          {CATEGORIES.map((cat) => (
            <Button
              key={cat.key}
              size="sm"
              variant={category === cat.key ? "default" : "outline"}
              onClick={() => setCategory(cat.key)}
              className="text-xs"
            >
              {cat.icon} {t(`admin.templates.categories.${cat.key}`)}
            </Button>
          ))}
        </div>
      </div>

      {viewMode === "catalog" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((tmpl) => (
            <Card key={tmpl.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push(`/admin/templates/${tmpl.id}`)}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <span className="text-2xl">{getCategoryIcon(tmpl.category)}</span>
                  <Badge className={tmpl.status === "published" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                    {tmpl.status}
                  </Badge>
                </div>
                <CardTitle className="text-base mt-2 line-clamp-2">{tmpl.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-muted-foreground line-clamp-2">{tmpl.description || "—"}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="font-semibold text-primary">{tmpl.base_price_rub} RUB</span>
                  <span className="text-xs text-muted-foreground">{t("admin.templates.cost_price")}: {tmpl.cost_price_rub} RUB</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  {tmpl.estimated_duration_sec && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" aria-hidden="true" />
                      {tmpl.estimated_duration_sec}s
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Zap className="h-3 w-3" aria-hidden="true" />
                    {getDifficultyLabel(tmpl.difficulty)}
                  </span>
                </div>
                {tmpl.tags && tmpl.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {tmpl.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                    ))}
                    {tmpl.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">+{tmpl.tags.length - 3}</Badge>
                    )}
                  </div>
                )}
                {(tmpl.success_rate !== null || tmpl.usage_count !== null) && (
                  <div className="flex items-center gap-3 text-xs border-t pt-2">
                    {tmpl.success_rate != null && (
                      <span className="flex items-center gap-1 text-green-600">
                        <TrendingUp className="h-3 w-3" aria-hidden="true" />
                        {(tmpl.success_rate * 100).toFixed(0)}%
                      </span>
                    )}
                    {tmpl.avg_rating != null && (
                      <span className="flex items-center gap-1 text-yellow-600">
                        <Star className="h-3 w-3" aria-hidden="true" />
                        {tmpl.avg_rating.toFixed(1)}
                      </span>
                    )}
                    {tmpl.usage_count != null && (
                      <span className="text-muted-foreground">{tmpl.usage_count}×</span>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm" aria-label="Templates table">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Code</th>
                    <th className="text-left py-3 px-4 font-medium">{t("admin.templates.name")}</th>
                    <th className="text-left py-3 px-4 font-medium">{t("admin.templates.category")}</th>
                    <th className="text-center py-3 px-4 font-medium">{t("admin.templates.status")}</th>
                    <th className="text-right py-3 px-4 font-medium">{t("admin.templates.price")}</th>
                    <th className="text-right py-3 px-4 font-medium">{t("admin.templates.cost_price")}</th>
                    <th className="text-right py-3 px-4 font-medium">{t("admin.templates.metrics")}</th>
                    <th className="text-right py-3 px-4 font-medium">{t("admin.templates.actions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((tmpl) => (
                    <tr key={tmpl.id} className="border-b last:border-0 hover:bg-muted/50">
                      <td className="py-3 px-4 font-mono text-xs">{tmpl.code}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span>{getCategoryIcon(tmpl.category)}</span>
                          <div>
                            <div className="font-medium">{tmpl.title}</div>
                            {tmpl.tags && tmpl.tags.length > 0 && (
                              <div className="flex gap-1 mt-1">
                                {tmpl.tags.slice(0, 2).map((tag) => (
                                  <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">{t(`admin.templates.categories.${tmpl.category || "all"}`)}</Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge className={tmpl.status === "published" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                          {tmpl.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-right font-medium">{tmpl.base_price_rub} RUB</td>
                      <td className="py-3 px-4 text-right text-muted-foreground">{tmpl.cost_price_rub} RUB</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2 text-xs">
                          {tmpl.success_rate != null && (
                            <span className="text-green-600">{(tmpl.success_rate * 100).toFixed(0)}%</span>
                          )}
                          {tmpl.avg_rating != null && (
                            <span className="text-yellow-600">⭐{tmpl.avg_rating.toFixed(1)}</span>
                          )}
                          {tmpl.usage_count != null && (
                            <span className="text-muted-foreground">{tmpl.usage_count}×</span>
                          )}
                        </div>
                      </td>
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
      )}

      {filtered.length === 0 && (
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">{t("admin.templates.no_templates")}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
