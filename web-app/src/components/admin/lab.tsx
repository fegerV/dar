"use client"

import { useState, useEffect, useCallback } from "react"
import { useTranslation } from "react-i18next"
import { FlaskConical, Play, CheckCircle, XCircle, Clock, Image as ImageIcon, Beaker, TrendingUp } from "lucide-react"

interface LabStats {
  total_scenarios: number
  total_photos: number
  total_benchmarks: number
  completed_benchmarks: number
  failed_benchmarks: number
  avg_quality_score: number | null
  avg_success_rate: number | null
  avg_cost: number | null
  proposals_approved: number
  proposals_applied: number
}

interface Scenario {
  id: string
  code: string
  name: string
  category: string | null
  difficulty: string | null
  is_active: boolean
}

interface Benchmark {
  id: string
  model_name: string
  status: string
  quality_score: number | null
  success_rate: number | null
  actual_cost: number | null
  scenario: Scenario | null
}

export function LabPanel() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<LabStats | null>(null)
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/admin/lab/stats")
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch {
      setError("API unavailable")
    }
  }, [])

  const fetchScenarios = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/admin/lab/scenarios")
      if (res.ok) {
        const data = await res.json()
        setScenarios(data)
      }
    } catch {
      setError("API unavailable")
    }
  }, [])

  const fetchBenchmarks = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/admin/lab/benchmarks")
      if (res.ok) {
        const data = await res.json()
        setBenchmarks(data)
      }
    } catch {
      setError("API unavailable")
    }
  }, [])

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      await Promise.all([fetchStats(), fetchScenarios(), fetchBenchmarks()])
      setLoading(false)
    }
    load()
  }, [fetchStats, fetchScenarios, fetchBenchmarks])

  const runAllBenchmarks = async () => {
    setRunning(true)
    try {
      const res = await fetch("/api/v1/admin/lab/benchmarks/run-all", { method: "POST" })
      if (res.ok) {
        await fetchBenchmarks()
        await fetchStats()
      }
    } catch {
      setError("Failed to run benchmarks")
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return <div className="p-6 text-muted-foreground">{t("common.loading", "Loading...")}</div>
  }

  if (error) {
    return <div className="p-6 text-destructive">{error}</div>
  }

  const statusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "running":
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FlaskConical className="h-6 w-6" />
            {t("admin.lab.title", "Video Generation Lab")}
          </h1>
          <p className="text-muted-foreground">
            {t("admin.lab.subtitle", "Benchmark scenarios, evaluate models, generate recipes")}
          </p>
        </div>
        <button
          onClick={runAllBenchmarks}
          disabled={running}
          className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          {running ? t("admin.lab.running", "Running...") : t("admin.lab.run_all", "Run All Benchmarks")}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <Beaker className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">{t("admin.lab.scenarios", "Scenarios")}</span>
          </div>
          <div className="text-2xl font-bold">{stats?.total_scenarios ?? 0}</div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <ImageIcon className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">{t("admin.lab.photos", "Photos")}</span>
          </div>
          <div className="text-2xl font-bold">{stats?.total_photos ?? 0}</div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <TrendingUp className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">{t("admin.lab.avg_quality", "Avg Quality")}</span>
          </div>
          <div className="text-2xl font-bold">
            {stats?.avg_quality_score != null ? (stats.avg_quality_score * 100).toFixed(0) + "%" : "—"}
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <CheckCircle className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">{t("admin.lab.success_rate", "Success Rate")}</span>
          </div>
          <div className="text-2xl font-bold">
            {stats?.avg_success_rate != null ? (stats.avg_success_rate * 100).toFixed(0) + "%" : "—"}
          </div>
        </div>
      </div>

      <div className="rounded-lg border">
        <div className="p-4 border-b">
          <h2 className="font-semibold">{t("admin.lab.scenarios_title", "Scenarios")}</h2>
        </div>
        <div className="divide-y">
          {scenarios.map((s) => (
            <div key={s.id} className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium">{s.name}</div>
                <div className="text-sm text-muted-foreground">
                  {s.code} · {s.category ?? "—"} · {s.difficulty ?? "—"}
                </div>
              </div>
              <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
              }`}>
                {s.is_active ? t("admin.lab.active", "Active") : t("admin.lab.inactive", "Inactive")}
              </span>
            </div>
          ))}
          {scenarios.length === 0 && (
            <div className="p-4 text-muted-foreground text-sm">{t("admin.lab.no_scenarios", "No scenarios found")}</div>
          )}
        </div>
      </div>

      <div className="rounded-lg border">
        <div className="p-4 border-b">
          <h2 className="font-semibold">{t("admin.lab.recent_benchmarks", "Recent Benchmarks")}</h2>
        </div>
        <div className="divide-y">
          {benchmarks.slice(0, 20).map((b) => (
            <div key={b.id} className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                {statusIcon(b.status)}
                <div>
                  <div className="font-medium">{b.model_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {b.scenario?.name ?? "—"} · {b.status}
                  </div>
                </div>
              </div>
              <div className="text-right text-sm">
                <div>
                  {t("admin.lab.quality", "Q")}: {b.quality_score != null ? (b.quality_score * 100).toFixed(0) + "%" : "—"}
                </div>
                <div className="text-muted-foreground">
                  ${b.actual_cost != null ? b.actual_cost.toFixed(3) : "—"}
                </div>
              </div>
            </div>
          ))}
          {benchmarks.length === 0 && (
            <div className="p-4 text-muted-foreground text-sm">{t("admin.lab.no_benchmarks", "No benchmarks yet")}</div>
          )}
        </div>
      </div>

      {stats && stats.proposals_approved > 0 && (
        <div className="rounded-lg border">
          <div className="p-4 border-b">
            <h2 className="font-semibold">{t("admin.lab.proposals", "Recipe Proposals")}</h2>
          </div>
          <div className="p-4">
            <div className="flex items-center gap-6 text-sm">
              <div>
                <span className="text-muted-foreground">{t("admin.lab.approved", "Approved")}: </span>
                <span className="font-semibold">{stats.proposals_approved}</span>
              </div>
              <div>
                <span className="text-muted-foreground">{t("admin.lab.applied", "Applied to Production")}: </span>
                <span className="font-semibold">{stats.proposals_applied}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
