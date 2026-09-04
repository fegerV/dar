"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiFetch } from "@/lib/api"
import type { AuditLog } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"

export function AdminAuditLogs() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const { items: logs, loading, page, pageSize, total, totalPages, setPage, setPageSize, setFilters } = useAdminList<AuditLog>({
    endpoint: "/admin/audit-logs",
    pageSize: 20,
    filters: search ? { search } : {},
    transform: (raw) => {
      const paginated = raw as { items: AuditLog[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(search ? { search } : {})
  }, [search, setFilters])

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Audit Logs</h1>
          <p className="text-muted-foreground mt-1">Historical record of all admin actions</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading audit logs...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Logs</h1>
        <p className="text-muted-foreground mt-1">Historical record of all admin actions</p>
      </div>

      <Card>
        <CardHeader>
          <div className="relative max-w-md">
            <Input
              placeholder="Filter by action..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              aria-label="Filter audit logs"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Audit logs table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Timestamp</th>
                  <th className="text-left py-3 px-4 font-medium">Action</th>
                  <th className="text-left py-3 px-4 font-medium">Actor</th>
                  <th className="text-left py-3 px-4 font-medium">Target</th>
                  <th className="text-left py-3 px-4 font-medium">IP</th>
                  <th className="text-left py-3 px-4 font-medium">User Agent</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="py-3 px-4 font-mono">{log.action}</td>
                    <td className="py-3 px-4">{log.actor_user_id ? `#${log.actor_user_id}` : "—"}</td>
                    <td className="py-3 px-4">
                      {log.target_type && log.target_id ? `${log.target_type} #${log.target_id}` : log.target_type ?? "—"}
                    </td>
                    <td className="py-3 px-4">{log.ip_address || "—"}</td>
                    <td className="py-3 px-4 max-w-xs truncate" title={log.user_agent || ""}>
                      {log.user_agent || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {logs.length === 0 && (
              <p className="py-6 text-center text-muted-foreground">No audit logs found.</p>
            )}
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
        </CardContent>
      </Card>
    </div>
  )
}
