"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { CheckCircle2, XCircle, RefreshCw } from "lucide-react"

interface StorageStats {
  provider: string
  healthy: boolean
  used_bytes: number
  total_bytes: number | null
  file_count: number
  error?: string
}

interface YandexConfig {
  oauth_token_set: boolean
  base_path: string
}

export function AdminStorage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<StorageStats | null>(null)
  const [yandexConfig, setYandexConfig] = useState<YandexConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadData = async () => {
    setLoading(true)
    try {
      const [storageStats, yandexCfg] = await Promise.all([
        apiFetch<StorageStats>("/admin/storage/stats").catch(() => null),
        apiFetch<YandexConfig>("/admin/storage/yandex/config").catch(() => null),
      ])
      setStats(storageStats)
      setYandexConfig(yandexCfg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadData()
  }, [user])

  const testConnection = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const result = await apiFetch<{ success: boolean; message: string }>("/admin/storage/yandex/test", {
        method: "POST",
      })
      setTestResult(result)
    } catch (e: unknown) {
      setTestResult({ success: false, message: (e as Error)?.message || "Connection failed" })
    } finally {
      setTesting(false)
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading storage...</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.sidebar.storage")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.pages.storage")}</p>
      </div>

      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Current Storage Provider</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p>
              <span className="text-muted-foreground">Provider:</span> {stats.provider}
            </p>
            <p className="flex items-center gap-2">
              <span className="text-muted-foreground">Status:</span>
              {stats.healthy ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-green-600" aria-hidden="true" />
                  <span className="text-green-600">Healthy</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 text-red-600" aria-hidden="true" />
                  <span className="text-red-600">Unavailable</span>
                </>
              )}
            </p>
            {stats.error && (
              <p className="text-red-600 text-sm">{stats.error}</p>
            )}
            <p>
              <span className="text-muted-foreground">Used:</span>{" "}
              {stats.used_bytes ? `${(stats.used_bytes / 1024 / 1024).toFixed(1)} MB` : "—"}
            </p>
            <p>
              <span className="text-muted-foreground">Files:</span> {stats.file_count}
            </p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t("admin.yandex_disk.title")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {t("admin.yandex_disk.subtitle")}
          </p>

          {yandexConfig && (
            <div className="space-y-3">
              <div>
                <Label>{t("admin.yandex_disk.token_status")}</Label>
                <div className="flex items-center gap-2 mt-1">
                  {yandexConfig.oauth_token_set ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-green-600" aria-hidden="true" />
                      <span className="text-green-600 text-sm">{t("admin.yandex_disk.token_configured")}</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-yellow-600" aria-hidden="true" />
                      <span className="text-yellow-600 text-sm">{t("admin.yandex_disk.token_not_configured")}</span>
                    </>
                  )}
                </div>
              </div>

              <div>
                <Label>{t("admin.yandex_disk.base_path")}</Label>
                <Input value={yandexConfig.base_path} disabled className="mt-1" />
              </div>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Button onClick={testConnection} disabled={testing} variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${testing ? "animate-spin" : ""}`} aria-hidden="true" />
              {testing ? t("admin.yandex_disk.testing") : t("admin.yandex_disk.test_connection")}
            </Button>
            <Button onClick={loadData} variant="ghost">
              {t("admin.yandex_disk.refresh")}
            </Button>
          </div>

          {testResult && (
            <div
              className={`p-3 rounded-md text-sm ${
                testResult.success
                  ? "bg-green-50 text-green-700 border border-green-200"
                  : "bg-red-50 text-red-700 border border-red-200"
              }`}
            >
              {testResult.message}
            </div>
          )}

          <div className="pt-4 border-t">
            <h3 className="font-medium mb-2">{t("admin.yandex_disk.how_to_title")}</h3>
            <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
              <li>{t("admin.yandex_disk.how_to_step_1")}</li>
              <li>{t("admin.yandex_disk.how_to_step_2")}</li>
              <li>{t("admin.yandex_disk.how_to_step_3")}</li>
              <li>{t("admin.yandex_disk.how_to_step_4")}</li>
              <li>{t("admin.yandex_disk.how_to_step_5")}</li>
              <li>{t("admin.yandex_disk.how_to_step_6")}</li>
              <li>{t("admin.yandex_disk.how_to_step_7")}</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
