"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import type { AdminPaymentDetailResponse } from "@/types/admin"

export default function AdminPaymentDetailPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [payment, setPayment] = useState<AdminPaymentDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (user && params.id) {
      setLoading(true)
      apiFetch<AdminPaymentDetailResponse>(`/admin/payments/${params.id}`)
        .then(setPayment)
        .catch(() => setPayment(null))
        .finally(() => setLoading(false))
    }
  }, [user, params.id])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading payment...</p>
  }

  if (!payment) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.payments")}</h1>
          <p className="text-muted-foreground mt-1">Payment {payment.id?.slice(0, 8)}…</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Payment Details</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p><span className="text-muted-foreground">ID:</span> <span className="font-mono">{payment.id}</span></p>
          <p><span className="text-muted-foreground">User ID:</span> <span className="font-mono">{payment.user_id || "—"}</span></p>
          <p><span className="text-muted-foreground">Amount:</span> {payment.amount_rub} ₽</p>
          <p><span className="text-muted-foreground">Method:</span> {payment.method}</p>
          <p><span className="text-muted-foreground">Status:</span> <Badge>{payment.status}</Badge></p>
          <p><span className="text-muted-foreground">Provider ID:</span> <span className="font-mono">{payment.provider_id || "—"}</span></p>
          <p><span className="text-muted-foreground">External ID:</span> <span className="font-mono">{payment.external_payment_id || "—"}</span></p>
          <p><span className="text-muted-foreground">Created:</span> {new Date(payment.created_at).toLocaleString()}</p>
          <p><span className="text-muted-foreground">Paid:</span> {payment.paid_at ? new Date(payment.paid_at).toLocaleString() : "—"}</p>
        </CardContent>
      </Card>
    </div>
  )
}
