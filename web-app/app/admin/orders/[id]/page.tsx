"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import type { AdminOrderDetailResponse } from "@/types/admin"

export default function AdminOrderDetailPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user, loading: authLoading } = useAdminAuth()
  const [order, setOrder] = useState<AdminOrderDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (user && params.id) {
      setLoading(true)
      apiFetch<AdminOrderDetailResponse>(`/admin/orders/${params.id}`)
        .then(setOrder)
        .catch(() => setOrder(null))
        .finally(() => setLoading(false))
    }
  }, [user, params.id])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading order...</p>
  }

  if (!order) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.orders")}</h1>
          <p className="text-muted-foreground mt-1">Order {order.id?.slice(0, 8)}…</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Order Details</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p><span className="text-muted-foreground">ID:</span> <span className="font-mono">{order.id}</span></p>
          <p><span className="text-muted-foreground">Project ID:</span> <span className="font-mono">{order.project_id}</span></p>
          <p><span className="text-muted-foreground">Status:</span> <Badge>{order.status}</Badge></p>
          <p><span className="text-muted-foreground">Cost:</span> {order.cost_rub} ₽</p>
          <p><span className="text-muted-foreground">Model:</span> {order.model_name || "—"}</p>
          <p><span className="text-muted-foreground">Error:</span> {order.error_code || "—"}</p>
          <p><span className="text-muted-foreground">Created:</span> {new Date(order.created_at).toLocaleString()}</p>
          <p><span className="text-muted-foreground">Completed:</span> {order.completed_at ? new Date(order.completed_at).toLocaleString() : "—"}</p>
        </CardContent>
      </Card>
    </div>
  )
}
