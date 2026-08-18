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

const initialHealth = [
  { name: "API", status: "🟢" },
  { name: "PostgreSQL", status: "🟢" },
  { name: "Redis", status: "🟢" },
  { name: "Queue", status: "🟢" },
  { name: "Workers", status: "🟢" },
  { name: "Storage", status: "🟢" },
  { name: "YooKassa", status: "🟠" },
  { name: "Telegram", status: "🟢" },
  { name: "AI Provider", status: "🟠" },
]

export function AdminSystem() {
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState<SystemSetting[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
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
      apiFetch<SystemSetting[]>("/admin/system/settings").catch(() => []),
      apiFetch<AuditLog[]>("/admin/audit-logs").catch(() => []),
    ]).then(([s, a]) => {
      setSettings(s)
      setAuditLogs(a)
    }).finally(() => setLoading(false))
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    await new Promise((resolve) => setTimeout(resolve, 800))
    setSaving(false)
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
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {initialHealth.map((item) => (
                  <div key={item.name} className="flex items-center justify-between rounded-lg border p-3">
                    <span className="text-sm font-medium">{item.name}</span>
                    <span className="text-lg">{item.status}</span>
                  </div>
                ))}
              </div>
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
