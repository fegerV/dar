"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Database, Cpu, Bot, HardDrive, Info, GitBranch } from "lucide-react"
import { useTranslation } from "react-i18next"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface HealthResponse {
  status: string
  database: boolean
  redis: boolean
  ai_providers: Record<string, boolean>
  storage: boolean
  disk: { total: number; used: number; free: number; used_percent: number }
  disk_alert: boolean
  queue_depth: Record<string, unknown>
  user_count: number | object
  components: Record<string, number>
}

interface DashboardStats {
  total_users: number
  total_projects: number
  total_payments: number
  pending_reviews: number
  active_generations: number
  running_jobs: number
  queued_jobs: number
  failed_jobs: number
  ai_cost_today: number
  revenue_today: number
  profit_today: number
}

export default function AdminHelpPage() {
  const { t } = useTranslation()
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [stats, setStats] = useState<DashboardStats | null>(null)
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
    setLoading(true)
    Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://localhost:8000"}/health/detailed`).then(r => r.ok ? r.json() : null).catch(() => null),
      apiFetch<DashboardStats>("/admin/stats").catch(() => null),
    ]).then(([h, s]) => {
      setHealth(h)
      setStats(s)
    }).finally(() => setLoading(false))
  }, [user])

  const formatBytes = (bytes: number) => {
    const units = ["B", "KB", "MB", "GB", "TB"]
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  if (authLoading) {
    return <p className="text-center py-8">{t("common.loading")}</p>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.system.help_title")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.system.help_subtitle")}</p>
      </div>

      <section>
        <h2 className="text-xl font-semibold mb-4">{t("admin.system.help_health")}</h2>
        {loading ? (
          <p className="text-sm text-muted-foreground">{t("admin.system.health_loading")}</p>
        ) : health ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_database")}</CardTitle>
                <Database className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.database ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                <CardDescription>{health.status}</CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Redis</CardTitle>
                <Cpu className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.redis ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_ai")}</CardTitle>
                <Bot className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Object.values(health.ai_providers).every(Boolean) ? "✅ " + t("common.ok") : "❌ " + t("common.error")}
                </div>
                {Object.entries(health.ai_providers).map(([name, healthy]) => (
                  <p key={name} className="text-xs text-muted-foreground">
                    {name}: {healthy ? "✅" : "❌"}
                  </p>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_storage")}</CardTitle>
                <HardDrive className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.storage ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_disk")}</CardTitle>
                <HardDrive className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.disk.used_percent.toFixed(1)}%</div>
                <CardDescription>
                  {t("admin.system.help_disk_used")}: {formatBytes(health.disk.used)} | {t("admin.system.help_disk_free")}: {formatBytes(health.disk.free)}
                </CardDescription>
                {health.disk_alert && (
                  <p className="text-xs text-red-500 mt-1">{t("admin.system.help_disk_alert")}</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_queue")}</CardTitle>
                <GitBranch className="h-5 w-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.queue_depth ? Object.keys(health.queue_depth).length : 0}</div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">{t("admin.system.health_unavailable")}</p>
        )}
      </section>

      {stats && (
        <section>
          <h2 className="text-xl font-semibold mb-4">Key Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_users")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_users.toLocaleString()}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_projects")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_projects.toLocaleString()}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_ai_cost")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.ai_cost_today.toLocaleString()} ₽</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t("admin.system.help_profit")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.profit_today.toLocaleString()} ₽</div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      <section>
        <h2 className="text-xl font-semibold mb-4">Admin Guide</h2>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                Quick Reference
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">System Health Dashboard</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Use the System page to monitor overall platform health, including database connectivity,
                  Redis cache, AI provider availability, storage, and disk usage. Red indicators require immediate attention.
                </p>
              </div>
              <div>
                <h3 className="font-medium mb-2">Feature Flags</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Feature flags control experimental functionality. New Recommendation Engine powers personalized
                  template suggestions. Video Lab enables advanced video effects (beta). Auto Moderation scans
                  uploaded content automatically.
                </p>
              </div>
              <div>
                <h3 className="font-medium mb-2">System Settings</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Generation settings control AI model defaults and timeouts. Payment settings configure Yookassa
                  integration. Always set a webhook secret for production. Notification settings control Telegram
                  and email delivery.
                </p>
              </div>
              <div>
                <h3 className="font-medium mb-2">Audit Logs</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  All admin actions are logged here for compliance and troubleshooting. Logs are retained for 90 days.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
