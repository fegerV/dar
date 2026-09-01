"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"

interface StorageStats {
  provider: string
  used_bytes: number
  total_bytes: number | null
  file_count: number
}

export function AdminStorage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<StorageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<StorageStats>("/admin/storage/stats")
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading storage...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">{t("admin.sidebar.storage")}</h1><p className="text-muted-foreground mt-1">{t("admin.pages.storage")}</p></div>
      {stats && (
        <Card>
          <CardHeader><CardTitle>Storage Provider</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <p><span className="text-muted-foreground">Provider:</span> {stats.provider}</p>
            <p><span className="text-muted-foreground">Used:</span> {stats.used_bytes ? `${(stats.used_bytes / 1024 / 1024).toFixed(1)} MB` : "—"}</p>
            <p><span className="text-muted-foreground">Total:</span> {stats.total_bytes ? `${(stats.total_bytes / 1024 / 1024 / 1024).toFixed(1)} GB` : "Unlimited"}</p>
            <p><span className="text-muted-foreground">Files:</span> {stats.file_count}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
