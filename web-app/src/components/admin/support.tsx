"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"

interface SupportTicket {
  id: string
  user_id: string
  order_id: string | null
  subject: string
  status: "open" | "in_progress" | "resolved" | "closed"
  priority: "low" | "medium" | "high" | "critical"
  created_at: string
  updated_at: string
  messages_count: number
}

export function AdminSupport() {
  const [tickets, setTickets] = useState<SupportTicket[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<SupportTicket[]>("/support/tickets?limit=100")
      .then(setTickets)
      .catch(() => setTickets([]))
      .finally(() => setLoading(false))
  }, [user])

  const statusColors = {
    open: "bg-blue-100 text-blue-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    resolved: "bg-green-100 text-green-800",
    closed: "bg-gray-100 text-gray-800",
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading support tickets...</p>
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Support</h1><p className="text-muted-foreground mt-1">User support tickets and conversations</p></div>
      <Card>
        <CardHeader><CardTitle>Tickets ({tickets.length})</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">ID</th><th className="text-left py-2">Subject</th><th className="text-left py-2">User</th><th className="text-center py-2">Priority</th><th className="text-center py-2">Status</th><th className="text-right py-2">Messages</th><th className="text-right py-2">Updated</th></tr></thead>
            <tbody>
              {tickets.map((t) => (
                <tr key={t.id} className="border-b">
                  <td className="py-2 font-mono">{t.id.slice(0, 8)}…</td>
                  <td className="py-2">{t.subject}</td>
                  <td className="py-2 font-mono">{t.user_id.slice(0, 8)}…</td>
                  <td className="py-2 text-center">
                    <Badge variant={t.priority === "critical" ? "destructive" : "secondary"}>{t.priority}</Badge>
                  </td>
                  <td className="py-2 text-center">
                    <Badge className={statusColors[t.status] || "bg-gray-100"}>{t.status}</Badge>
                  </td>
                  <td className="py-2 text-right">{t.messages_count}</td>
                  <td className="py-2 text-right text-xs">{new Date(t.updated_at).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
