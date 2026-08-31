"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import type { AdminLedgerResponse } from "@/types/admin"

const TRANSACTION_TYPES = ["adjustment", "bonus", "refund", "penalty", "payment", "spend"]

export function AdminLedger() {
  const [data, setData] = useState<AdminLedgerResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState<string>("")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadTransactions = async (type?: string, page: number = 1) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set("page", String(page))
      if (type) params.set("transaction_type", type)
      const resp = await apiFetch<AdminLedgerResponse>(`/admin/ledger/transactions?${params.toString()}`)
      setData(resp)
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadTransactions()
  }, [user])

  const handleTypeFilter = (type: string) => {
    setTypeFilter(type)
    loadTransactions(type || undefined, 1)
  }

  const handlePage = (page: number) => {
    if (data) {
      loadTransactions(typeFilter || undefined, page)
    }
  }

  const formatAmount = (amount: number, isBonus: boolean) => {
    return `${amount.toFixed(2)} ₽${isBonus ? " (bonus)" : ""}`
  }

  const getTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading transactions...</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Transaction History</h1>
        <p className="text-muted-foreground mt-1">Ledger transactions and wallet adjustments</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge
              variant={typeFilter === "" ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => handleTypeFilter("")}
            >
              All Types
            </Badge>
            {TRANSACTION_TYPES.map((t) => (
              <Badge
                key={t}
                variant={typeFilter === t ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => handleTypeFilter(t)}
              >
                {getTypeLabel(t)}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Transactions ({data?.total || 0}) — Page {data?.page || 1}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!data || data.transactions.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">No transactions found.</p>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">ID</th>
                      <th className="text-left py-2">Type</th>
                      <th className="text-right py-2">Amount</th>
                      <th className="text-left py-2">User</th>
                      <th className="text-left py-2">Email</th>
                      <th className="text-left py-2">Reason</th>
                      <th className="text-left py-2">Admin</th>
                      <th className="text-left py-2">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.transactions.map((tx) => (
                      <tr key={tx.id} className="border-b">
                        <td className="py-2 font-mono">{tx.id.slice(0, 8)}…</td>
                        <td className="py-2">
                          <Badge variant="outline">{getTypeLabel(tx.type)}</Badge>
                          {tx.is_bonus && <Badge variant="secondary" className="ml-1">Bonus</Badge>}
                        </td>
                        <td className="py-2 text-right">{formatAmount(tx.amount_rub, tx.is_bonus)}</td>
                        <td className="py-2">{tx.user_id ? tx.user_id.slice(0, 8) + "…" : "—"}</td>
                        <td className="py-2">{tx.user_email || "—"}</td>
                        <td className="py-2">{tx.reason || "—"}</td>
                        <td className="py-2">{tx.admin_id ? tx.admin_id.slice(0, 8) + "…" : "—"}</td>
                        <td className="py-2">{new Date(tx.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {data.total > (data.page_size || 20) && (
                <div className="flex justify-center gap-2 mt-4">
                  {Array.from(
                    { length: Math.ceil(data.total / (data.page_size || 20)) },
                    (_, i) => i + 1
                  ).map((p) => (
                    <button
                      key={p}
                      className={`px-3 py-1 rounded text-sm ${
                        p === data.page ? "bg-primary text-primary-foreground" : "border hover:bg-accent"
                      }`}
                      onClick={() => handlePage(p)}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
