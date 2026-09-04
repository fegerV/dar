"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"

interface SupportTicket {
  id: string
  user_id: string
  order_id: string | null
  subject: string
  status: "open" | "in_progress" | "resolved" | "closed"
  priority: "low" | "medium" | "high" | "critical"
  created_at: string
  updated_at: string
  messages_count: number
}

export function AdminSupport() {
  const { t } = useTranslation()
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const { items: tickets, loading, page, pageSize, total, totalPages, setPage, setPageSize } = useAdminList<SupportTicket>({
    endpoint: "/admin/support/tickets",
    pageSize: 20,
    transform: (raw) => {
      const paginated = raw as { items: SupportTicket[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  const statusColors = {
    open: "bg-blue-100 text-blue-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    resolved: "bg-green-100 text-green-800",
    closed: "bg-gray-100 text-gray-800",
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading support tickets...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">{t("admin.sidebar.support")}</h1><p className="text-muted-foreground mt-1">{t("admin.pages.support")}</p></div>
      <Card>
        <CardHeader><CardTitle>Tickets ({total})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b"><th className="text-left py-2">ID</th><th className="text-left py-2">Subject</th><th className="text-left py-2">User</th><th className="text-center py-2">Priority</th><th className="text-center py-2">Status</th><th className="text-right py-2">Messages</th><th className="text-right py-2">Updated</th></tr></thead>
              <tbody>
                {tickets.map((t) => (
                  <tr key={t.id} className="border-b">
                    <td className="py-2 font-mono">{t.id.slice(0, 8)}…</td>
                    <td className="py-2">{t.subject}</td>
                    <td className="py-2 font-mono">{t.user_id.slice(0, 8)}…</td>
                    <td className="py-2 text-center">
                      <Badge variant={t.priority === "critical" ? "destructive" : "secondary"}>{t.priority}</Badge>
                    </td>
                    <td className="py-2 text-center">
                      <Badge className={statusColors[t.status] || "bg-gray-100"}>{t.status}</Badge>
                    </td>
                    <td className="py-2 text-right">{t.messages_count}</td>
                    <td className="py-2 text-right text-xs">{new Date(t.updated_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
                {tickets.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-muted-foreground">No tickets found</td>
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
