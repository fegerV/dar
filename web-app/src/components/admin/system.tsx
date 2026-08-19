"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AuditLog, SystemSetting } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface HealthStatus {
  name: string
  status: "healthy" | "degraded" | "down"
  detail?: string
}

const statusEmoji: Record<HealthStatus["status"], string> = {
  healthy: "🟢",
  degraded: "🟠",
  down: "🔴",
}

export function AdminSystem() {
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState<SystemSetting[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [health, setHealth] = useState<HealthStatus[]>([])
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
      setSettings(s)
      setAuditLogs(a)
    }).finally(() => setLoading(false))
  }, [user])

  useEffect(() => {
    if (!user) return
    setHealthLoading(true)
    apiFetch<{ components: Record<string, { status: string; detail?: string }> } | HealthStatus[] | { services: HealthStatus[] }>(
      "/health/detailed"
    ).then((data) => {
      let statuses: HealthStatus[] = []
      if (Array.isArray(data)) {
        statuses = data.map((d) => ({
          name: d.name,
          status: mapStatus(d.status),
          detail: d.detail,
        }))
      } else if ("components" in data) {
        statuses = Object.entries(data.components).map(([name, info]) => ({
          name,
          status: mapStatus(info.status),
          detail: info.detail,
        }))
      } else if ("services" in data) {
        statuses = data.services.map((s) => ({
          name: s.name,
          status: mapStatus(s.status),
          detail: s.detail,
        }))
      }
      setHealth(statuses)
    }).catch(() => {
      setHealth([])
    }).finally(() => setHealthLoading(false))
  }, [user])

  function mapStatus(s: string): HealthStatus["status"] {
    const lower = s.toLowerCase()
    if (lower.includes("down") || lower.includes("fail") || lower.includes("error")) return "down"
    if (lower.includes("degrad") || lower.includes("warn")) return "degraded"
    return "healthy"
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      for (const setting of settings) {
        const input = document.getElementById(setting.key) as HTMLInputElement | null
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
      await new Promise((resolve) => setTimeout(resolve, 300))
    } finally {
      setSaving(false)
    }
  }

  if (authLoading) {
    return <p className="text-center py-8">Checking admin access...</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System</h1>
        <p className="text-muted-foreground mt-1">Logs, audit, settings</p>
      </div>

      <Tabs defaultValue="health">
        <TabsList>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Health</CardTitle>
            </CardHeader>
            <CardContent>
              {healthLoading ? (
                <p className="text-sm text-muted-foreground">Loading health status...</p>
              ) : health.length === 0 ? (
                <p className="text-sm text-muted-foreground">Health endpoint unavailable</p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {health.map((item) => (
                    <div key={item.name} className="flex items-center justify-between rounded-lg border p-3">
                      <span className="text-sm font-medium">{item.name}</span>
                      <span className="text-lg">{statusEmoji[item.status] || "❔"}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {settings.map((setting) => (
                <div key={setting.id} className="grid gap-2">
                  <Label htmlFor={setting.key}>{setting.key}</Label>
                  <Input
                    id={setting.key}
                    defaultValue={JSON.stringify(setting.value)}
                    aria-label={setting.key}
                  />
                  {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
                </div>
              ))}
              <Button onClick={handleSave} disabled={saving} className="w-full">
                <Save className="h-4 w-4 mr-2" aria-hidden="true" />
                {saving ? "Saving..." : "Save Settings"}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>Recent Audit Logs</CardTitle>
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
