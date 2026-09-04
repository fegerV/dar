"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { useToast } from "@/components/ui/toast"

interface AnalyticsData {
  total_events: number
  events_by_type: Record<string, number>
  days: number
}

export function AdminAnalytics() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState("7")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadAnalytics = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (startDate) params.set("start_date", startDate)
      if (endDate) params.set("end_date", endDate)
      else if (period) params.set("days", period)
      const d = await apiFetch<AnalyticsData>(`/admin/analytics?${params.toString()}`)
      setData(d)
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [startDate, endDate, period])

  useEffect(() => {
    if (user) loadAnalytics()
  }, [user, loadAnalytics])

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (startDate) params.set("start_date", startDate)
      if (endDate) params.set("end_date", endDate)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/admin/analytics/export?${params.toString()}`, {
        credentials: "include",
      })
      if (!res.ok) throw new Error("Export failed")
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "analytics.csv"
      a.click()
      window.URL.revokeObjectURL(url)
      toast({ title: t("notification.success") || "Success", description: "Analytics exported", variant: "success" })
    } catch {
      toast({ title: t("notification.error") || "Error", description: "Export failed", variant: "error" })
    }
  }

  function BarChart({ data: chartData }: {
    data: Array<{ label: string; value: number }>;
  }) {
    const maxVal = Math.max(...chartData.map(d => d.value), 1)
    return (
      <div className="space-y-2">
        {chartData.map((d) => {
          const pct = (d.value / maxVal) * 100
          return (
            <div key={d.label} className="flex items-center gap-2">
              <span className="text-xs w-24 text-right">{d.label}</span>
              <div className="flex-1 bg-muted rounded-full h-6 relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-end pr-2">
                  <span className="text-xs font-medium">{d.value}</span>
                </div>
                <div className="h-full bg-primary rounded-full" style={{ width: `${pct}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading analytics...</p>
  }

  if (!data) return null

  const eventEntries = Object.entries(data.events_by_type || {})
    .map(([type, count]) => ({ label: type, value: count }))
    .sort((a, b) => b.value - a.value)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.analytics")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.analytics")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-auto" aria-label="Start date" />
          <span className="text-muted-foreground">—</span>
          <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-auto" aria-label="End date" />
          <Select value={period} onValueChange={setPeriod} className="w-[120px]" aria-label="Period selector">
            <option value="7">7 days</option>
            <option value="30">30 days</option>
            <option value="90">90 days</option>
          </Select>
          <Button variant="outline" onClick={exportCSV}>Export CSV</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Total Events</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold">{data.total_events.toLocaleString()}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Event Types</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold">{eventEntries.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Period</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold">{data.days || period} days</p></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Events by Type</CardTitle></CardHeader>
        <CardContent>
          {eventEntries.length > 0 ? <BarChart data={eventEntries} /> : <p className="text-sm text-muted-foreground">No data</p>}
        </CardContent>
      </Card>
    </div>
  )
}
