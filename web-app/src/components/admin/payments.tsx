"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import type { AdminPayment } from "@/types/admin"

export function AdminPayments() {
  const [payments, setPayments] = useState<AdminPayment[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadPayments = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<AdminPayment[]>("/admin/payments")
      setPayments(data)
    } catch {
      setPayments([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadPayments()
  }, [user])

  const refund = async (id: string, amount?: number) => {
    const amt = amount ? `?amount_rub=${amount}` : ""
    if (!confirm("Refund this payment?")) return
    try {
      await apiFetch(`/payments/${id}/refund${amt}&reason=admin_refund`, { method: "POST" })
      loadPayments()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Refund failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading payments...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Payments</h1><p className="text-muted-foreground mt-1">Payment transactions and refunds</p></div>
      <Card>
        <CardHeader><CardTitle>Payments ({payments.length})</CardTitle></CardHeader>
        <CardContent>
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
                    {p.status === "paid" && (
                      <Button size="sm" variant="ghost" aria-label={`Refund payment ${p.id}`} onClick={() => refund(p.id)}>
                        Refund
                      </Button>
                    )}
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
