"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useRouter, useParams } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import type { AdminUser, UserWallet } from "@/types/admin"

interface UserActivity {
  id: string
  action: string
  target_type: string | null
  target_id: string | null
  created_at: string
  ip_address: string | null
}

export function AdminUserDetail() {
  const [user, setUser] = useState<AdminUser | null>(null)
  const [wallet, setWallet] = useState<UserWallet | null>(null)
  const [activity, setActivity] = useState<UserActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("overview")
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const { user: currentUser, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !currentUser) router.push("/admin/login")
  }, [authLoading, currentUser, router])

  const loadUser = async () => {
    setLoading(true)
    try {
      const [u, w, a] = await Promise.all([
        apiFetch<AdminUser>(`/admin/users/${params.id}`),
        apiFetch<UserWallet>(`/admin/users/${params.id}/wallet`),
        apiFetch<UserActivity[]>(`/admin/audit-logs?actor_user_id=${params.id}&limit=50`).catch(() => []),
      ])
      setUser(u)
      setWallet(w)
      setActivity(a)
    } catch {
      // stay
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentUser && params.id) loadUser()
  }, [currentUser, params.id])

  const adjustWallet = async (amount: number, type: string, reason: string) => {
    if (!reason || reason.length < 5) {
      alert("Reason must be at least 5 characters")
      return
    }
    if (!confirm(`Adjust wallet by ${amount} ₽ (${type})?`)) return
    try {
      await apiFetch(`/users/${params.id}/wallet/adjust`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount_rub: amount, type, reason }),
      })
      alert("Wallet adjusted")
      loadUser()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Adjustment failed")
    }
  }

  const impersonate = async () => {
    const mfaToken = prompt("Enter MFA token for impersonation:")
    if (!mfaToken) return
    try {
      const res = await apiFetch<{ access_token: string; refresh_token: string; impersonation: boolean }>(
        `/users/${params.id}/impersonate?${new URLSearchParams({ mfa_token: mfaToken })}`
      )
      alert("Impersonation started (5-min limit). Close session to end.")
      localStorage.setItem("impersonate_token", res.access_token)
      router.push(`/impersonate/${params.id}`)
    } catch (e: unknown) {
      alert((e as Error)?.message || "Impersonation failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading user...</p>
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{user.display_name || "User"}</h1>
          <p className="text-muted-foreground mt-1">{user.email || "No email"}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.back()}>Back</Button>
          {currentUser?.is_admin && (
            <Button variant="outline" onClick={impersonate}>Impersonate</Button>
          )}
        </div>
      </div>

      <div className="flex gap-2 border-b">
        {["overview", "wallet", "activity"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm ${activeTab === tab ? "border-b-2 border-primary font-medium" : "text-muted-foreground"}`}
            aria-label={`Tab ${tab}`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <Card>
          <CardHeader><CardTitle>User Info</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <p><span className="text-muted-foreground">ID:</span> <span className="font-mono">{user.id}</span></p>
            <p><span className="text-muted-foreground">Status:</span> <Badge variant={user.status === "active" ? "default" : "secondary"}>{user.status}</Badge></p>
            <p><span className="text-muted-foreground">Admin:</span> {user.is_admin ? "Yes" : "No"}</p>
            <p><span className="text-muted-foreground">Phone:</span> {user.phone || "—"}</p>
            <p><span className="text-muted-foreground">Locale:</span> {user.locale || "—"}</p>
            <p><span className="text-muted-foreground">Registered:</span> {new Date(user.created_at).toLocaleString()}</p>
          </CardContent>
        </Card>
      )}

      {activeTab === "wallet" && (
        <Card>
          <CardHeader><CardTitle>Wallet</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {wallet && (
              <div>
                <p className="text-2xl font-bold">{wallet.balance_rub.toFixed(2)} ₽</p>
                <p className="text-sm text-muted-foreground">Bonus: {wallet.bonus_balance.toFixed(2)} ₽</p>
                <p className="text-xs text-muted-foreground">Updated: {wallet.updated_at ? new Date(wallet.updated_at).toLocaleString() : "—"}</p>
              </div>
            )}
            <div className="flex gap-2">
              <Input type="number" placeholder="Amount" id="adjust_AMOUNT" aria-label="Amount" />
              <select id="adjust_TYPE" aria-label="Transaction type" className="border rounded px-2">
                <option value="adjustment">Adjustment</option>
                <option value="bonus">Bonus</option>
                <option value="refund">Refund</option>
                <option value="penalty">Penalty</option>
              </select>
              <Input placeholder="Reason (min 5 chars)" id="adjust_REASON" aria-label="Reason" />
            </div>
            <Button onClick={() => {
              const amount = parseFloat((document.getElementById("adjust_AMOUNT") as HTMLInputElement)?.value || "0")
              const type = (document.getElementById("adjust_TYPE") as HTMLSelectElement)?.value || "adjustment"
              const reason = (document.getElementById("adjust_REASON") as HTMLInputElement)?.value || ""
              if (amount > 0) adjustWallet(amount, type, reason)
            }}>
              Adjust Wallet
            </Button>
          </CardContent>
        </Card>
      )}

      {activeTab === "activity" && (
        <Card>
          <CardHeader><CardTitle>Audit Activity</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {activity.map((entry) => (
                <div key={entry.id} className="border-b pb-2 text-sm">
                  <span className="font-mono">{entry.action}</span>
                  <span className="text-muted-foreground"> — {entry.target_type || ""}</span>
                  <span className="text-xs text-muted-foreground float-right">{new Date(entry.created_at).toLocaleString()}</span>
                </div>
              ))}
              {activity.length === 0 && <p className="text-sm text-muted-foreground">No activity</p>}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
