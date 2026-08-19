"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface AIProvider {
  name: string
  healthy: boolean
  latency_ms: number | null
  cost: string
  daily_usage: number
  monthly_usage: number
}

interface AIProviderResponse {
  providers: AIProvider[]
}

export function AdminAI() {
  const [providers, setProviders] = useState<AIProvider[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<AIProviderResponse>("/ai/providers/status")
      .then(data => setProviders(data.providers || []))
      .catch(() => setProviders([]))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading AI providers...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">AI Models & Providers</h1><p className="text-muted-foreground mt-1">Provider status, latency, and costs</p></div>
      <Card>
        <CardHeader><CardTitle>Providers ({providers.length})</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Name</th><th className="text-center py-2">Status</th><th className="text-right py-2">Latency</th><th className="text-right py-2">Cost</th><th className="text-right py-2">Daily</th><th className="text-right py-2">Monthly</th><th className="text-right py-2">Actions</th></tr></thead>
            <tbody>
              {providers.map((p) => (
                <tr key={p.name} className="border-b">
                  <td className="py-2">{p.name}</td>
                  <td className="py-2 text-center">
                    <Badge variant={p.healthy ? "default" : "destructive"}>{p.healthy ? "Healthy" : "Down"}</Badge>
                  </td>
                  <td className="py-2 text-right">{p.latency_ms ? `${p.latency_ms}ms` : "—"}</td>
                  <td className="py-2 text-right">{p.cost}</td>
                  <td className="py-2 text-right">{p.daily_usage}</td>
                  <td className="py-2 text-right">{p.monthly_usage}</td>
                  <td className="py-2 text-right">
                    <Button size="sm" variant="ghost" aria-label={`Test ${p.name}`}>Test</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
