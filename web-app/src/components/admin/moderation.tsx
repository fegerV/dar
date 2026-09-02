"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"

interface ModerationItem {
  id: string
  type: "user" | "prompt" | "photo" | "brief" | "generation"
  status: "pending" | "approved" | "rejected" | "escalated"
  created_at: string
  updated_at: string
  content_preview: string
}

export function AdminModeration() {
  const { t } = useTranslation()
  const [items, setItems] = useState<ModerationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("pending")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    setLoading(true)
    apiFetch<ModerationItem[]>(`/admin/moderation/items?status=${filter}`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false))
  }, [user, filter])

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
        <CardHeader><CardTitle>Queue ({items.length})</CardTitle></CardHeader>
        <CardContent>
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
                    <Button size="sm" variant="ghost" aria-label={`View ${item.id}`}>View</Button>
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
