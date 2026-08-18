"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Eye, RefreshCw } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminPayment } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

const statusColors: Record<string, string> = {
  paid: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  failed: "bg-red-100 text-red-800",
  refunded: "bg-gray-100 text-gray-800",
}

export function AdminPayments() {
  const [search, setSearch] = useState("")
  const [payments, setPayments] = useState<AdminPayment[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<AdminPayment[]>("/admin/payments")
      .then(setPayments)
      .catch(() => setPayments([]))
      .finally(() => setLoading(false))
  }, [user])

  const filtered = payments.filter((p) => {
    if (search && !p.id.toLowerCase().includes(search.toLowerCase()) && !(p.user_id || "").toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Payments</h1>
          <p className="text-muted-foreground mt-1">Payments and wallet ledger</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading payments...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Payments</h1>
        <p className="text-muted-foreground mt-1">Payments and wallet ledger</p>
      </div>

      <Card>
        <CardHeader>
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Search payments..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              aria-label="Search payments"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Payments table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">User</th>
                  <th className="text-right py-3 px-4 font-medium">Amount</th>
                  <th className="text-left py-3 px-4 font-medium">Provider</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-left py-3 px-4 font-medium">Date</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((payment) => (
                  <tr key={payment.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{payment.id}</td>
                    <td className="py-3 px-4">{(payment.user_id || "—").slice(0, 8)}</td>
                    <td className="py-3 px-4 text-right">{payment.amount_rub} ₽</td>
                    <td className="py-3 px-4">{payment.method}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={statusColors[payment.status] || "bg-gray-100"}>
                        {payment.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">{payment.created_at ? new Date(payment.created_at).toLocaleDateString() : "—"}</td>
                    <td className="py-3 px-4 text-right">
                      <Button size="sm" variant="ghost" aria-label={`View payment ${payment.id}`}>
                        <Eye className="h-4 w-4" aria-hidden="true" />
                      </Button>
                      {payment.status === "failed" && (
                        <Button size="sm" variant="ghost" aria-label={`Refund payment ${payment.id}`}>
                          <RefreshCw className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      )}
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

