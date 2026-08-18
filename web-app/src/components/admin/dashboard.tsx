"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Users, ShoppingCart, Sparkles, Cpu, DollarSign, TrendingUp, AlertTriangle, CheckCircle2, XCircle } from "lucide-react"

const stats = [
  { title: "Users", value: "12 482", icon: Users, color: "text-blue-600" },
  { title: "Orders", value: "1 842", icon: ShoppingCart, color: "text-green-600" },
  { title: "Generations", value: "3 921", icon: Sparkles, color: "text-purple-600" },
  { title: "Revenue", value: "1 248 500 ₽", icon: DollarSign, color: "text-emerald-600" },
  { title: "AI Cost", value: "183 400 ₽", icon: Cpu, color: "text-orange-600" },
  { title: "Profit", value: "1 065 100 ₽", icon: TrendingUp, color: "text-teal-600" },
]

const jobStats = [
  { label: "Running", value: 17, status: "running", icon: CheckCircle2, color: "text-green-600" },
  { label: "Queued", value: 42, status: "queued", icon: AlertTriangle, color: "text-yellow-600" },
  { label: "Failed", value: 3, status: "failed", icon: XCircle, color: "text-red-600" },
  { label: "Completed", value: 318, status: "completed", icon: CheckCircle2, color: "text-gray-600" },
]

const workers = [
  { name: "video-worker-01", gpu: "RTX4090", vram: "21/24 GB", jobs: 2, status: "🟢" },
  { name: "video-worker-02", gpu: "V100", vram: "28/32 GB", jobs: 1, status: "🟢" },
  { name: "video-worker-03", gpu: "V100", vram: "31/32 GB", jobs: 1, status: "🟡" },
  { name: "worker-04", gpu: "—", vram: "—", jobs: 0, status: "🔴" },
]

export function AdminDashboard() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Operational center overview</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => {
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
            <CardTitle>Generations Now</CardTitle>
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
            <CardTitle>GPU / Workers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {workers.map((worker) => (
                <div key={worker.name} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{worker.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {worker.gpu} · {worker.vram} · {worker.jobs} jobs
                    </p>
                  </div>
                  <span className="text-lg">{worker.status}</span>
                </div>
              ))}
            </div>
            <Button className="w-full mt-4" variant="outline">
              View All Workers
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>AI Cost vs Revenue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Today</span>
              <span>Margin: 85.3%</span>
            </div>
            <Progress value={85.3} aria-label="Profit margin 85.3%" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>AI Cost: 183 400 ₽</span>
              <span>Revenue: 1 248 500 ₽</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
