"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, Info, Database, Cpu, Bot, HardDrive, GitBranch, BarChart3 } from "lucide-react"
import { useTranslation } from "react-i18next"
import { apiFetch } from "@/lib/api"
import type { AuditLog, SystemSetting } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface DetailedHealthResponse {
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

const statusIcons: Record<string, React.ReactNode> = {
  database: <Database className="h-5 w-5" />,
  redis: <Cpu className="h-5 w-5" />,
  ai: <Bot className="h-5 w-5" />,
  storage: <HardDrive className="h-5 w-5" />,
  disk: <HardDrive className="h-5 w-5" />,
}

const settingDescriptions: Record<string, Record<string, { label: string; description: string; recommended: string }>> = {
  feature_flags: {
    NEW_RECOMMENDATION_ENGINE: {
      label: "admin.system.flag_new_recommendation_engine",
      description: "admin.system.flag_new_recommendation_engine_desc",
      recommended: "admin.system.flag_new_recommendation_engine_rec",
    },
    NEW_TEMPLATE_EDITOR: {
      label: "admin.system.flag_new_template_editor",
      description: "admin.system.flag_new_template_editor_desc",
      recommended: "admin.system.flag_new_template_editor_rec",
    },
    VIDEO_LAB: {
      label: "admin.system.flag_video_lab",
      description: "admin.system.flag_video_lab_desc",
      recommended: "admin.system.flag_video_lab_rec",
    },
    AUTO_MODERATION: {
      label: "admin.system.flag_auto_moderation",
      description: "admin.system.flag_auto_moderation_desc",
      recommended: "admin.system.flag_auto_moderation_rec",
    },
  },
  generation: {
    default_model: {
      label: "admin.system.setting_default_model",
      description: "admin.system.setting_default_model_desc",
      recommended: "admin.system.setting_default_model_rec",
    },
    max_retries: {
      label: "admin.system.setting_max_retries",
      description: "admin.system.setting_max_retries_desc",
      recommended: "admin.system.setting_max_retries_rec",
    },
    queue_timeout_sec: {
      label: "admin.system.setting_queue_timeout_sec",
      description: "admin.system.setting_queue_timeout_sec_desc",
      recommended: "admin.system.setting_queue_timeout_sec_rec",
    },
    generation_timeout_sec: {
      label: "admin.system.setting_generation_timeout_sec",
      description: "admin.system.setting_generation_timeout_sec_desc",
      recommended: "admin.system.setting_generation_timeout_sec_rec",
    },
  },
  payments: {
    yookassa_enabled: {
      label: "admin.system.setting_yookassa_enabled",
      description: "admin.system.setting_yookassa_enabled_desc",
      recommended: "admin.system.setting_yookassa_enabled_rec",
    },
    yookassa_webhook_secret: {
      label: "admin.system.setting_yookassa_webhook_secret",
      description: "admin.system.setting_yookassa_webhook_secret_desc",
      recommended: "admin.system.setting_yookassa_webhook_secret_rec",
    },
  },
  notifications: {
    telegram_enabled: {
      label: "admin.system.setting_telegram_enabled",
      description: "admin.system.setting_telegram_enabled_desc",
      recommended: "admin.system.setting_telegram_enabled_rec",
    },
    email_enabled: {
      label: "admin.system.setting_email_enabled",
      description: "admin.system.setting_email_enabled_desc",
      recommended: "admin.system.setting_email_enabled_rec",
    },
  },
}

const settingGroupInfo: Record<string, { label: string; description: string }> = {
  feature_flags: {
    label: "admin.system.setting_feature_flags",
    description: "admin.system.setting_feature_flags_desc",
  },
  generation: {
    label: "admin.system.setting_generation",
    description: "admin.system.setting_generation_desc",
  },
  payments: {
    label: "admin.system.setting_payments",
    description: "admin.system.setting_payments_desc",
  },
  notifications: {
    label: "admin.system.setting_notifications",
    description: "admin.system.setting_notifications_desc",
  },
}

export function AdminSystem() {
  const { t } = useTranslation()
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState<SystemSetting[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [health, setHealth] = useState<DetailedHealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [healthLoading, setHealthLoading] = useState(true)
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
      apiFetch<SystemSetting[]>("/admin/system/settings").catch(() => []),
      apiFetch<AuditLog[]>("/admin/audit-logs").catch(() => []),
    ]).then(([s, a]) => {
      setSettings(s || [])
      setAuditLogs(a || [])
    }).finally(() => setLoading(false))
  }, [user])

  useEffect(() => {
    if (!user) return
    setHealthLoading(true)
    apiFetch<DetailedHealthResponse>("/health/detailed")
      .then((data) => {
        setHealth(data)
      })
      .catch(() => {
        setHealth(null)
      })
      .finally(() => setHealthLoading(false))
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    try {
      for (const setting of settings) {
        const input = document.getElementById(`setting-${setting.key}`) as HTMLInputElement | null
        if (input && input.value !== JSON.stringify(setting.value)) {
          await apiFetch<SystemSetting>(`/admin/system/settings/${setting.key}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value: JSON.parse(input.value) }),
          })
        }
      }
      const data = await apiFetch<SystemSetting[]>("/admin/system/settings")
      setSettings(data || [])
    } finally {
      setSaving(false)
    }
  }

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

  const formatPercent = (used: number, total: number) => {
    return total > 0 ? ((used / total) * 100).toFixed(1) : "0"
  }

  if (authLoading) {
    return <p className="text-center py-8">{t("common.loading")}</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.system.title")}</h1>
        <p className="text-muted-foreground mt-1">{t("admin.system.subtitle")}</p>
      </div>

      <Tabs defaultValue="health">
        <TabsList>
          <TabsTrigger value="health">{t("admin.system.health")}</TabsTrigger>
          <TabsTrigger value="flags">{t("admin.system.flags")}</TabsTrigger>
          <TabsTrigger value="settings">{t("admin.system.settings")}</TabsTrigger>
          <TabsTrigger value="logs">{t("admin.system.logs")}</TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="space-y-4">
          {healthLoading ? (
            <p className="text-sm text-muted-foreground">{t("admin.system.health_loading")}</p>
          ) : health ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_database")}</CardTitle>
                  {statusIcons.database}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{health.database ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                  <p className="text-xs text-muted-foreground">{health.status}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_redis")}</CardTitle>
                  {statusIcons.redis}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{health.redis ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_ai")}</CardTitle>
                  {statusIcons.ai}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{Object.values(health.ai_providers).every(Boolean) ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                  {Object.entries(health.ai_providers).map(([name, healthy]) => (
                    <div key={name} className="text-xs text-muted-foreground">
                      {name}: {healthy ? "✅" : "❌"}
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_storage")}</CardTitle>
                  {statusIcons.storage}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{health.storage ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_disk")}</CardTitle>
                  {statusIcons.disk}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatPercent(health.disk.used, health.disk.total)}%</div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                    <div>{t("admin.system.help_disk_used")}: {formatBytes(health.disk.used)}</div>
                    <div>{t("admin.system.help_disk_free")}: {formatBytes(health.disk.free)}</div>
                  </div>
                  {health.disk_alert && (
                    <p className="text-xs text-red-500 mt-2">{t("admin.system.help_disk_alert")}</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_queue")}</CardTitle>
                  <GitBranch className="h-5 w-5" />
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                      <div className="text-lg font-bold">{health.components["database"]}</div>
                      <div className="text-xs text-muted-foreground">{t("admin.system.help_running")}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{t("admin.system.help_users")}</CardTitle>
                  <BarChart3 className="h-5 w-5" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{typeof health.user_count === "number" ? health.user_count : "—"}</div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">{t("admin.system.health_unavailable")}</p>
          )}
        </TabsContent>

        <TabsContent value="flags" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("admin.system.features_title")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {settings.filter((s) => s.key === "feature_flags").map((setting) => {
                const flags = setting.value as Record<string, boolean>
                const flagInfo = settingDescriptions.feature_flags
                return (
                  <div key={setting.id} className="space-y-3">
                    {Object.entries(flags).map(([flag, value]) => {
                      const info = flagInfo[flag]
                      return (
                        <div key={flag} className="flex items-center justify-between rounded-lg border p-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <Label htmlFor={flag} className="font-medium">
                                {info ? t(info.label) : flag}
                              </Label>
                              <Info className="h-4 w-4 text-muted-foreground" />
                            </div>
                            {info && (
                              <>
                                <p className="text-xs text-muted-foreground mt-1">{t(info.description)}</p>
                                <p className="text-xs text-blue-500 mt-1">{t(info.recommended)}</p>
                              </>
                            )}
                          </div>
                          <input
                            id={flag}
                            type="checkbox"
                            checked={value}
                            onChange={(e) => {
                              const newFlags = { ...flags, [flag]: e.target.checked }
                              const settingInput = document.getElementById(`setting-${setting.key}`) as HTMLInputElement
                              if (settingInput) settingInput.value = JSON.stringify({ ...newFlags })
                            }}
                            aria-label={`Toggle ${info ? t(info.label) : flag}`}
                          />
                        </div>
                      )
                    })}
                    <input type="hidden" id={`setting-${setting.key}`} defaultValue={JSON.stringify(setting.value)} />
                  </div>
                )
              })}
              <Button onClick={handleSave} disabled={saving} className="w-full">
                <Save className="h-4 w-4 mr-2" aria-hidden="true" />
                {saving ? t("admin.system.saving") : t("admin.system.save_flags")}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("admin.system.settings_title")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {settings
                .filter((s) => !["feature_flags"].includes(s.key))
                .map((setting) => {
                  const groupInfo = settingGroupInfo[setting.key]
                  return (
                    <div key={setting.id} className="space-y-3 rounded-lg border p-4">
                      <div>
                        <Label htmlFor={setting.key} className="text-lg font-medium">
                          {groupInfo ? t(groupInfo.label) : setting.key}
                        </Label>
                        {groupInfo && (
                          <CardDescription className="mt-1">{t(groupInfo.description)}</CardDescription>
                        )}
                      </div>
                      {renderSettingFields(setting, settingDescriptions[setting.key], t)}
                      <input type="hidden" id={`setting-${setting.key}`} defaultValue={JSON.stringify(setting.value)} />
                    </div>
                  )
                })}
              <Button onClick={handleSave} disabled={saving} className="w-full">
                <Save className="h-4 w-4 mr-2" aria-hidden="true" />
                {saving ? t("admin.system.saving") : t("admin.system.save_settings")}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>{t("admin.system.logs")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {auditLogs.length === 0 && !loading && (
                  <p className="text-sm text-muted-foreground text-center py-4">No audit logs</p>
                )}
                {auditLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-3 rounded-md border p-3 text-sm">
                    <span className="text-muted-foreground min-w-[80px]">{new Date(log.created_at).toLocaleTimeString()}</span>
                    <span className="font-mono text-muted-foreground min-w-[60px]">{log.action}</span>
                    <span className="flex-1">{log.target_type || ""} #{log.target_id?.slice(0, 8) || ""}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

function renderSettingFields(setting: SystemSetting, fieldInfo?: Record<string, { label: string; description: string; recommended: string }>, t?: (key: string) => string) {
  const value = setting.value as Record<string, unknown>
  return Object.entries(value).map(([key, val]) => {
      const info = fieldInfo?.[key]
      const inputId = `${setting.key}-${key}`
      return (
      <div key={key} className="grid gap-2">
        <Label htmlFor={inputId} className="flex items-center gap-2">
          {info ? t!(info.label) : key}
          <Info className="h-4 w-4 text-muted-foreground" />
        </Label>
        <div className="text-xs text-muted-foreground space-y-1">
          {info && (
            <>
              <p>{t!(info.description)}</p>
              <p className="text-blue-500">{t!(info.recommended)}</p>
            </>
          )}
        </div>
        <Input
          id={inputId}
          defaultValue={typeof val === "object" ? JSON.stringify(val) : String(val)}
          aria-label={info ? t!(info.label) : key}
        />
      </div>
    )
  })
}
