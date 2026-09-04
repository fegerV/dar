"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Search, Eye } from "lucide-react"
import { useTranslation } from "react-i18next"
import type { AdminOrder } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"

const statusColors: Record<string, string> = {
  READY: "bg-green-100 text-green-800",
  GENERATING: "bg-blue-100 text-blue-800",
  FAILED: "bg-red-100 text-red-800",
  QUEUED: "bg-yellow-100 text-yellow-800",
}

export function AdminOrders() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const filters = useMemo(() => {
    const f: Record<string, string | number | boolean | undefined> = {}
    if (statusFilter !== "all") f.status = statusFilter
    if (startDate) f.start_date = startDate
    if (endDate) f.end_date = endDate
    return f
  }, [statusFilter, startDate, endDate])
  const filtersKey = JSON.stringify(filters)

  const { items: orders, loading, page, pageSize, total, setPage, setPageSize, setFilters } = useAdminList<AdminOrder>({
    endpoint: "/admin/orders",
    pageSize: 20,
    filters,
    transform: (raw) => {
      const paginated = raw as { items: AdminOrder[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(filters)
  }, [filters, filtersKey, setFilters])

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (startDate) params.set("start_date", startDate)
      if (endDate) params.set("end_date", endDate)
      if (statusFilter !== "all") params.set("status", statusFilter)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/admin/orders/export?${params.toString()}`, {
        credentials: "include",
      })
      if (!res.ok) throw new Error("Export failed")
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "orders.csv"
      a.click()
      window.URL.revokeObjectURL(url)
      toast({ title: t("notification.success") || "Success", description: "Orders exported", variant: "success" })
    } catch {
      toast({ title: t("notification.error") || "Error", description: "Export failed", variant: "error" })
    }
  }

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.orders")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.orders")}</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading orders...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.sidebar.orders")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.pages.orders")}</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
              <Input
                placeholder="Search orders..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
                aria-label="Search orders"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-[180px]" aria-label="Filter by status">
              <option value="all">All</option>
              <option value="READY">Ready</option>
              <option value="GENERATING">Generating</option>
              <option value="FAILED">Failed</option>
              <option value="QUEUED">Queued</option>
            </Select>
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-auto" aria-label="Start date" />
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-auto" aria-label="End date" />
            <Button variant="outline" onClick={exportCSV}>Export CSV</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Orders table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">User</th>
                  <th className="text-left py-3 px-4 font-medium">Template</th>
                  <th className="text-left py-3 px-4 font-medium">Status</th>
                  <th className="text-right py-3 px-4 font-medium">Amount</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{order.id}</td>
                    <td className="py-3 px-4">{order.requested_by_user_id || "—"}</td>
                    <td className="py-3 px-4">{order.template_version_id || "—"}</td>
                    <td className="py-3 px-4">
                      <Badge className={statusColors[order.status] || "bg-gray-100"}>{order.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Button size="sm" variant="ghost" aria-label={`View order ${order.id}`} onClick={() => router.push(`/admin/orders/${order.id}`)}>
                          <Eye className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">No orders found</td>
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
