"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"

interface ModerationItem {
  id: string
  type: "user" | "prompt" | "photo" | "brief" | "generation"
  status: "pending" | "approved" | "rejected" | "escalated"
  created_at: string
  updated_at: string
  content_preview: string
  title?: string | null
  description?: string | null
  video_url?: string | null
  thumbnail_url?: string | null
  user_id?: string
  project_id?: string
}

export function AdminModeration() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [filter, setFilter] = useState("pending")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()
  const [selectedItem, setSelectedItem] = useState<ModerationItem | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const { items, loading, page, pageSize, total, setPage, setPageSize, setFilters, refetch } = useAdminList<ModerationItem>({
    endpoint: "/admin/moderation/items",
    pageSize: 20,
    filters: { status: filter },
    transform: (raw) => {
      const paginated = raw as { items: ModerationItem[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters({ status: filter })
  }, [filter, setFilters])

  const openItem = async (item: ModerationItem) => {
    setDetailLoading(true)
    try {
      const data = await apiFetch<ModerationItem>(`/admin/moderation/items/${item.id}`)
      setSelectedItem(data)
    } catch {
      setSelectedItem(item)
    } finally {
      setDetailLoading(false)
    }
  }

  const performAction = async (action: "approve" | "reject" | "escalate") => {
    if (!selectedItem) return
    setActionLoading(true)
    try {
      await apiFetch(`/admin/moderation/items/${selectedItem.id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, reason: "" }),
      })
      toast({ title: t("notification.success") || "Success", description: `Item ${action}d`, variant: "success" })
      setSelectedItem(null)
      refetch()
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : `Failed to ${action} item`
      toast({ title: t("notification.error") || "Error", description: message, variant: "error" })
    } finally {
      setActionLoading(false)
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading moderation queue...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">{t("admin.sidebar.moderation")}</h1><p className="text-muted-foreground mt-1">{t("admin.pages.moderation")}</p></div>
      <div className="flex gap-2">
        {["pending", "approved", "rejected", "escalated"].map((s) => (
          <Button key={s} variant={filter === s ? "default" : "ghost"} onClick={() => setFilter(s)}>
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </Button>
        ))}
      </div>
      <Card>
        <CardHeader><CardTitle>Queue ({total})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b"><th className="text-left py-2">ID</th><th className="text-left py-2">Type</th><th className="text-left py-2">Preview</th><th className="text-center py-2">Status</th><th className="text-right py-2">Created</th><th className="text-right py-2">Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2 font-mono">{item.id.slice(0, 8)}…</td>
                    <td className="py-2">{item.type}</td>
                    <td className="py-2 max-w-xs truncate">{item.content_preview}</td>
                    <td className="py-2 text-center">
                      <Badge variant={item.status === "approved" ? "default" : item.status === "rejected" ? "destructive" : "secondary"}>{item.status}</Badge>
                    </td>
                    <td className="py-2 text-right text-xs">{new Date(item.created_at).toLocaleDateString()}</td>
                    <td className="py-2 text-right">
                      <Button size="sm" variant="ghost" onClick={() => openItem(item)}>Review</Button>
                    </td>
                  </tr>
                ))}
                {items.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">No items found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
        </CardContent>
      </Card>

      <Dialog open={!!selectedItem} onOpenChange={(open) => !open && setSelectedItem(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Moderate {selectedItem?.id?.slice(0, 8)}…</DialogTitle>
            <DialogDescription>
              {selectedItem?.type} — {selectedItem?.status}
            </DialogDescription>
          </DialogHeader>
          {detailLoading ? (
            <p className="py-4 text-center text-muted-foreground">Loading...</p>
          ) : selectedItem ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-muted-foreground">Title:</span> {selectedItem.title || "—"}</div>
                <div><span className="text-muted-foreground">User:</span> <span className="font-mono">{selectedItem.user_id?.slice(0, 8)}…</span></div>
                <div><span className="text-muted-foreground">Project:</span> <span className="font-mono">{selectedItem.project_id?.slice(0, 8)}…</span></div>
                <div><span className="text-muted-foreground">Created:</span> {new Date(selectedItem.created_at).toLocaleString()}</div>
              </div>
              {selectedItem.description && (
                <Card>
                  <CardHeader><CardTitle>Description</CardTitle></CardHeader>
                  <CardContent><p className="text-sm whitespace-pre-wrap">{selectedItem.description}</p></CardContent>
                </Card>
              )}
              {selectedItem.thumbnail_url && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Thumbnail</p>
                  <img src={selectedItem.thumbnail_url} alt="thumbnail" className="max-h-40 rounded border" />
                </div>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="default" onClick={() => performAction("approve")} disabled={actionLoading || selectedItem.status === "approved"}>Approve</Button>
                <Button variant="destructive" onClick={() => performAction("reject")} disabled={actionLoading || selectedItem.status === "rejected"}>Reject</Button>
                <Button variant="outline" onClick={() => performAction("escalate")} disabled={actionLoading || selectedItem.status === "escalated"}>Escalate</Button>
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  )
}
