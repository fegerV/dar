"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Play } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminOrder } from "@/types/admin"
import { useAdminAuth } from "@/contexts/admin-auth-context"

const statusColors: Record<string, string> = {
  READY: "bg-green-100 text-green-800",
  GENERATING: "bg-blue-100 text-blue-800",
  FAILED: "bg-red-100 text-red-800",
  QUEUED: "bg-yellow-100 text-yellow-800",
}

export function AdminOrderDetail() {
  const router = useRouter()
  const params = useParams()
  const orderId = params.id as string
  const [order, setOrder] = useState<AdminOrder | null>(null)
  const [loading, setLoading] = useState(true)
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user || !orderId) return
    apiFetch<AdminOrder>(`/admin/orders/${orderId}`)
      .then(setOrder)
      .catch(() => setOrder(null))
      .finally(() => setLoading(false))
  }, [user, orderId])

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Order</h1>
          <p className="text-muted-foreground mt-1">Loading order details...</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!order) {
    return (
      <div className="space-y-6">
        <Button onClick={() => router.back()} variant="ghost" aria-label="Go back">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <p className="text-muted-foreground">Order not found.</p>
      </div>
    )
  }

  const videoUrl = order.output_json?.video_url
  const hasVideo = typeof videoUrl === "string" && videoUrl.length > 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Order #{order.id}</h1>
          <p className="text-muted-foreground mt-1">Order details and generation output</p>
        </div>
        <Button variant="ghost" onClick={() => router.back()} aria-label="Go back">
          <ArrowLeft className="h-4 w-4" />
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Status</span>
            <Badge className={statusColors[order.status] || "bg-gray-100"}>{order.status}</Badge>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Cost</span>
            <p className="font-medium">{order.cost_rub} &#8381;</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Model</span>
            <p className="font-medium">{order.model_name || "—"}</p>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Template Version</span>
            <p className="font-medium">{order.template_version_id || "—"}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Full Lifecycle Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-3 py-2">
              <span className="text-xs text-muted-foreground min-w-[80px]">Order created</span>
              <span>{new Date(order.created_at).toLocaleString()}</span>
            </div>
            {order.error_code && (
              <div className="flex items-start gap-3 py-2">
                <span className="text-xs text-muted-foreground min-w-[80px]">Error</span>
                <span className="text-red-600">{order.error_code}</span>
              </div>
            )}
            {order.completed_at && (
              <div className="flex items-start gap-3 py-2">
                <span className="text-xs text-muted-foreground min-w-[80px]">Completed</span>
                <span>{new Date(order.completed_at).toLocaleString()}</span>
              </div>
            )}
            <div className="flex items-start gap-3 py-2">
              <span className="text-xs text-muted-foreground min-w-[80px]">Status</span>
              <Badge className={statusColors[order.status] || "bg-gray-100"}>{order.status}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Input</CardTitle>
        </CardHeader>
        <CardContent>
          {order.input_json ? (
            <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-60 overflow-y-auto">{JSON.stringify(order.input_json, null, 2)}</pre>
          ) : (
            <p className="text-muted-foreground">—</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Output</CardTitle>
        </CardHeader>
        <CardContent>
          {order.output_json ? (
            <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-60 overflow-y-auto">{JSON.stringify(order.output_json, null, 2)}</pre>
          ) : (
            <p className="text-muted-foreground">—</p>
          )}
        </CardContent>
      </Card>

      {hasVideo && (
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <video
              src={videoUrl as string}
              controls
              className="w-full max-w-2xl rounded-md"
              aria-label="Video preview"
            >
              Your browser does not support the video tag.
            </video>
            <div className="mt-3">
              <Button aria-label="Open video in new tab">
                <Play className="h-4 w-4 mr-2" />
                Open video
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
