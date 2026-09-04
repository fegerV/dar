"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { Eye } from "lucide-react"
import type { AdminPayment } from "@/types/admin"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"

export function AdminPayments() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const filters = useMemo(() => {
    const f: Record<string, string | number | boolean | undefined> = {}
    if (startDate) f.start_date = startDate
    if (endDate) f.end_date = endDate
    if (statusFilter !== "all") f.status = statusFilter
    return f
  }, [startDate, endDate, statusFilter])
  const filtersKey = JSON.stringify(filters)

  const { items: payments, loading, page, pageSize, total, setPage, setPageSize, setFilters, refetch } = useAdminList<AdminPayment>({
    endpoint: "/admin/payments",
    pageSize: 20,
    filters,
    transform: (raw) => {
      const paginated = raw as { items: AdminPayment[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(filters)
  }, [filters, filtersKey, setFilters])

  const refund = async (id: string, amount?: number) => {
    const amt = amount ? `?amount_rub=${amount}` : ""
    if (!confirm("Refund this payment?")) return
    try {
      await apiFetch(`/payments/${id}/refund${amt}&reason=admin_refund`, { method: "POST" })
      toast({
        title: t("notification.success") || "Success",
        description: "Payment refunded successfully",
        variant: "success",
      })
      refetch()
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Refund failed"
      toast({
        title: t("notification.error") || "Error",
        description: message,
        variant: "error",
      })
    }
  }

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (startDate) params.set("start_date", startDate)
      if (endDate) params.set("end_date", endDate)
      if (statusFilter !== "all") params.set("status", statusFilter)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/admin/payments/export?${params.toString()}`, {
        credentials: "include",
      })
      if (!res.ok) throw new Error("Export failed")
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "payments.csv"
      a.click()
      window.URL.revokeObjectURL(url)
      toast({ title: t("notification.success") || "Success", description: "Payments exported", variant: "success" })
    } catch {
      toast({ title: t("notification.error") || "Error", description: "Export failed", variant: "error" })
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading payments...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">{t("admin.sidebar.payments")}</h1><p className="text-muted-foreground mt-1">{t("admin.pages.payments")}</p></div>
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4">
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-auto" aria-label="Start date" />
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-auto" aria-label="End date" />
            <Select value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-[180px]" aria-label="Filter by status">
              <option value="all">All</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
              <option value="refunded">Refunded</option>
              <option value="failed">Failed</option>
            </Select>
            <Button variant="outline" onClick={exportCSV}>Export CSV</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b"><th className="text-left py-2">ID</th><th className="text-left py-2">User</th><th className="text-right py-2">Amount</th><th className="text-left py-2">Method</th><th className="text-center py-2">Status</th><th className="text-right py-2">Actions</th></tr></thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id} className="border-b">
                    <td className="py-2 font-mono">{p.id.slice(0, 8)}…</td>
                    <td className="py-2">{p.user_id ? p.user_id.slice(0, 8) + "…" : "—"}</td>
                    <td className="py-2 text-right">{p.amount_rub.toFixed(2)} ₽</td>
                    <td className="py-2">{p.method}</td>
                    <td className="py-2 text-center">
                      <Badge variant={p.status === "paid" ? "default" : "secondary"}>{p.status}</Badge>
                    </td>
                     <td className="py-2 text-right">
                      <div className="flex justify-end gap-2">
                        <Button size="sm" variant="ghost" aria-label={`View payment ${p.id}`} onClick={() => router.push(`/admin/payments/${p.id}`)}>
                          <Eye className="h-4 w-4" aria-hidden="true" />
                        </Button>
                       {p.status === "paid" && (
                         <Button size="sm" variant="ghost" aria-label={`Refund payment ${p.id}`} onClick={() => refund(p.id)}>
                           Refund
                         </Button>
                       )}
                      </div>
                     </td>
                  </tr>
                ))}
                {payments.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">No payments found</td>
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
