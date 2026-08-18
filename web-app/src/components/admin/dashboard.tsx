"use client"

import { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Users, ShoppingCart, Sparkles, Cpu, DollarSign, TrendingUp, AlertTriangle, CheckCircle2, XCircle } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { DashboardStats } from "@/types/admin"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useRouter } from "next/navigation"

export function AdminDashboard() {
  const { user, loading: authLoading, error } = useAdminAuth()
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user && !error) {
      router.push("/admin/login")
    }
  }, [authLoading, user, error, router])

  useEffect(() => {
    if (!user) return
    apiFetch<DashboardStats>("/admin/stats")
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading || loading || !stats) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Operational center overview</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">—</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">—</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const summaryCards = [
    { title: "Users", value: stats.total_users.toLocaleString(), icon: Users, color: "text-blue-600" },
    { title: "Orders", value: stats.total_projects.toLocaleString(), icon: ShoppingCart, color: "text-green-600" },
    { title: "Generations", value: stats.total_payments.toLocaleString(), icon: Sparkles, color: "text-purple-600" },
    { title: "Revenue", value: stats.revenue_today.toLocaleString() + " \u20BD", icon: DollarSign, color: "text-emerald-600" },
    { title: "AI Cost", value: stats.ai_cost_today.toLocaleString() + " \u20BD", icon: Cpu, color: "text-orange-600" },
    { title: "Profit", value: stats.profit_today.toLocaleString() + " \u20BD", icon: TrendingUp, color: "text-teal-600" },
  ]

  const jobStats = [
    { label: "Running", value: stats.running_jobs, status: "running", icon: CheckCircle2, color: "text-green-600" },
    { label: "Queued", value: stats.queued_jobs, status: "queued", icon: AlertTriangle, color: "text-yellow-600" },
    { label: "Failed", value: stats.failed_jobs, status: "failed", icon: XCircle, color: "text-red-600" },
    { label: "Completed", value: stats.total_projects - stats.failed_jobs - stats.running_jobs - stats.queued_jobs, status: "completed", icon: CheckCircle2, color: "text-gray-600" },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Operational center overview</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {summaryCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} aria-hidden="true" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Jobs Now</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {jobStats.map((stat) => {
                const Icon = stat.icon
                return (
                  <div key={stat.label} className="flex items-center space-x-3 rounded-lg border p-3">
                    <Icon className={`h-5 w-5 ${stat.color}`} aria-hidden="true" />
                    <div>
                      <p className="text-sm font-medium">{stat.label}</p>
                      <p className="text-2xl font-bold">{stat.value}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profit Margin</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Today</span>
              {stats.revenue_today > 0 && (
                <span>Margin: {((stats.profit_today / stats.revenue_today) * 100).toFixed(1)}%</span>
              )}
            </div>
            {stats.revenue_today > 0 && <Progress value={(stats.profit_today / stats.revenue_today) * 100} aria-label="Profit margin" />}
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>AI Cost: {stats.ai_cost_today.toLocaleString()} ₽</span>
              <span>Revenue: {stats.revenue_today.toLocaleString()} ₽</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
