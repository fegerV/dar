"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, RefreshCw } from "lucide-react"

const systemHealth = [
  { name: "API", status: "🟢" },
  { name: "PostgreSQL", status: "🟢" },
  { name: "Redis", status: "🟢" },
  { name: "Queue", status: "🟢" },
  { name: "Workers", status: "🟢" },
  { name: "Storage", status: "🟢" },
  { name: "YooKassa", status: "🟢" },
  { name: "Telegram", status: "🟢" },
  { name: "AI Provider", status: "🟠" },
]

const settings = [
  { key: "max_generation_duration_sec", value: 300, description: "Max generation duration" },
  { key: "default_template", value: "birthday_v1", description: "Default template" },
  { key: "max_retries", value: 3, description: "Max retries for failed jobs" },
]

export function AdminSystem() {
  const { t } = useTranslation()
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    await new Promise((resolve) => setTimeout(resolve, 800))
    setSaving(false)
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
                {systemHealth.map((item) => (
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
                <div key={setting.key} className="grid gap-2">
                  <Label htmlFor={setting.key}>{setting.key}</Label>
                  <Input
                    id={setting.key}
                    defaultValue={String(setting.value)}
                    aria-label={setting.key}
                  />
                  <p className="text-xs text-muted-foreground">{setting.description}</p>
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
              <CardTitle>Recent Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { time: "12:34:10", level: "INFO", message: "Worker video-worker-01 heartbeat OK" },
                  { time: "12:34:05", level: "WARN", message: "Generation #89212 quality gate retry 2/3" },
                  { time: "12:33:58", level: "INFO", message: "Payment PAY-004 received via YooKassa" },
                  { time: "12:33:42", level: "ERROR", message: "Queue job #88102 failed: timeout on step render" },
                  { time: "12:33:30", level: "INFO", message: "User 18372 updated profile" },
                ].map((log, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-md border p-3 text-sm">
                    <span className="text-muted-foreground">{log.time}</span>
                    <span className={`font-mono ${log.level === "ERROR" ? "text-red-600" : log.level === "WARN" ? "text-yellow-600" : "text-green-600"}`}>{log.level}</span>
                    <span className="flex-1">{log.message}</span>
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
