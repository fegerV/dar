"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Plus, Save, X } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"

interface WebhookEndpoint {
  id: string
  url: string
  events: string[]
  is_active: boolean
  created_at: string
}

const EVENT_TYPES = ["payment.completed", "payment.failed", "generation.completed", "generation.failed", "webhook.delivery", "user.registered"]

export function AdminWebhooks() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [editing, setEditing] = useState<WebhookEndpoint | null>(null)
  const [draft, setDraft] = useState<Partial<WebhookEndpoint>>({})
  const [saving, setSaving] = useState(false)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const { items: webhooks, loading, page, pageSize, total, totalPages, setPage, setPageSize, refetch } = useAdminList<WebhookEndpoint>({
    endpoint: "/admin/webhooks",
    pageSize: 20,
    transform: (raw) => {
      const paginated = raw as { items: WebhookEndpoint[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  const save = async () => {
    if (!draft.url) {
      toast({
        title: t("notification.error") || "Error",
        description: "URL is required",
        variant: "error",
      })
      return
    }
    setSaving(true)
    try {
      if (editing) {
        await apiFetch<WebhookEndpoint>(`/admin/webhooks/${editing.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: draft.url, events: draft.events, is_active: draft.is_active }),
        })
      } else {
        await apiFetch<WebhookEndpoint>("/admin/webhooks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: draft.url, events: draft.events, is_active: draft.is_active ?? true }),
        })
      }
      setEditing(null)
      setDraft({})
      toast({
        title: t("notification.success") || "Success",
        description: editing ? "Webhook updated" : "Webhook created",
        variant: "success",
      })
      refetch()
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Save failed"
      toast({
        title: t("notification.error") || "Error",
        description: message,
        variant: "error",
      })
    } finally {
      setSaving(false)
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading webhooks...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold">Webhooks</h1><p className="text-muted-foreground mt-1">Configure webhook endpoints</p></div>
        <Button onClick={() => { setEditing(null); setDraft({}) }}>
          <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
          New Webhook
        </Button>
      </div>

      {editing !== null && (
        <Card>
          <CardHeader><CardTitle>{editing.id ? "Edit Webhook" : "New Webhook"}</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><Label>URL</Label><Input value={draft.url || ""} onChange={e => setDraft({ ...draft, url: e.target.value })} aria-label="Webhook URL" placeholder="https://example.com/webhook" /></div>
            <div>
              <Label>Events</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {EVENT_TYPES.map((evt) => (
                  <label key={evt} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={draft.events?.includes(evt) ?? false}
                      onChange={(e) => {
                        const events = draft.events || []
                        if (e.target.checked) events.push(evt)
                        else events.splice(events.indexOf(evt), 1)
                        setDraft({ ...draft, events: [...events] })
                      }}
                      aria-label={evt}
                    />
                    {evt}
                  </label>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="wh_active" checked={draft.is_active ?? true} onChange={e => setDraft({ ...draft, is_active: e.target.checked })} aria-label="Active" />
              <Label htmlFor="wh_active">Active</Label>
            </div>
            <div className="flex gap-2">
              <Button onClick={save} disabled={saving}>{saving ? "Saving..." : (<><Save className="h-4 w-4 mr-2" aria-hidden="true" />Save</>)}</Button>
              <Button variant="ghost" onClick={() => { setEditing(null); setDraft({}) }}><X className="h-4 w-4" aria-hidden="true" /></Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Webhooks ({total})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b"><th className="text-left py-2">URL</th><th className="text-left py-2">Events</th><th className="text-center py-2">Status</th><th className="text-right py-2">Actions</th></tr></thead>
              <tbody>
                {webhooks.map((wh) => (
                  <tr key={wh.id} className="border-b">
                    <td className="py-2 break-all">{wh.url}</td>
                    <td className="py-2">{wh.events?.join(", ") || "—"}</td>
                    <td className="py-2 text-center">
                      <Badge variant={wh.is_active ? "default" : "secondary"}>{wh.is_active ? "Active" : "Inactive"}</Badge>
                    </td>
                    <td className="py-2 text-right">
                      <Button size="sm" variant="ghost" aria-label={`Edit webhook ${wh.id}`} onClick={() => setEditing(wh)}>Edit</Button>
                    </td>
                  </tr>
                ))}
                {webhooks.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-muted-foreground">No webhooks found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
        </CardContent>
      </Card>
    </div>
  )
}
