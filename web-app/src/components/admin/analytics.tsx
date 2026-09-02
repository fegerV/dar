"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"

interface AnalyticsData {
  total_generations: number
  total_revenue: number
  total_new_users: number
  generation_status_breakdown: Record<string, number>
  cost_by_model: Record<string, { count: number; cost: number }>
  daily_revenue: Record<string, number>
  daily_generations: Record<string, Record<string, number>>
}

export function AdminAnalytics() {
  const { t } = useTranslation()
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState("7")
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const d = await apiFetch<AnalyticsData>(`/admin/analytics?days=${period}`)
      setData(d)
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadAnalytics()
  }, [user, period, loadAnalytics])

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
        <Select value={period} onValueChange={setPeriod} className="w-[120px]" aria-label="Period selector">
          <option value="7">7 days</option>
          <option value="30">30 days</option>
          <option value="90">90 days</option>
        </Select>
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
