"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Search, Eye, Wallet, LogIn } from "lucide-react"
import { apiFetch } from "@/lib/api"
import type { AdminUser, UserWallet, AdminPayment } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

export function AdminUsers() {
  const [search, setSearch] = useState("")
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  const [wallet, setWallet] = useState<UserWallet | null>(null)
  const [walletLoading, setWalletLoading] = useState(false)
  const [payments, setPayments] = useState<AdminPayment[]>([])
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    apiFetch<AdminUser[]>("/admin/users")
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false))
  }, [user])

  const openWallet = async (userId: string) => {
    setSelectedUserId(userId)
    setWallet(null)
    setPayments([])
    setWalletLoading(true)
    try {
      const w = await apiFetch<UserWallet>(`/admin/users/${userId}/wallet`)
      setWallet(w)
      const pay = await apiFetch<AdminPayment[]>("/admin/payments")
      setPayments(pay.filter((p) => p.user_id === userId))
    } catch {
      setWallet(null)
      setPayments([])
    } finally {
      setWalletLoading(false)
    }
  }

  const closeWallet = () => {
    setSelectedUserId(null)
    setWallet(null)
    setWalletLoading(false)
  }

  const handleImpersonate = async (userId: string) => {
    const mfaToken = prompt("Enter MFA token for impersonation:")
    if (!mfaToken) return
    try {
      const data = await apiFetch<{ access_token: string; refresh_token: string; impersonation: boolean }>(
        `/admin/users/${userId}/impersonate?${new URLSearchParams({ mfa_token: mfaToken })}`
      )
      if (data.impersonation) {
        localStorage.setItem("impersonate_token", data.access_token)
        alert("Impersonation started (5-min TTL)")
      } else {
        localStorage.setItem("daragent_admin_access", data.access_token)
        document.cookie = `daragent_admin_access=${data.access_token}; path=/; max-age=300; SameSite=Lax; Secure`
        window.location.href = "/admin/dashboard"
      }
    } catch (err: unknown) {
      console.error("Impersonate failed:", (err as Error)?.message)
    }
  }

  const filtered = users.filter((u) => {
    if (search && !u.display_name?.toLowerCase().includes(search.toLowerCase()) && !u.email?.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Users</h1>
          <p className="text-muted-foreground mt-1">Manage users and segments</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading users...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-muted-foreground mt-1">Manage users and segments</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
              <Input
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
                aria-label="Search users"
              />
            </div>
            <Button variant="outline">Segments</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Users table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">Name</th>
                  <th className="text-left py-3 px-4 font-medium">Email</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-center py-3 px-4 font-medium">Admin</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => (
                  <tr key={u.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{u.id}</td>
                    <td className="py-3 px-4">{u.display_name || "—"}</td>
                    <td className="py-3 px-4">{u.email || "—"}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={u.status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                        {u.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {u.is_admin ? (
                        <Badge className="bg-purple-100 text-purple-800">Yes</Badge>
                      ) : (
                        <span className="text-muted-foreground">No</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                      <Button size="sm" variant="ghost" aria-label={`View user ${u.id}`} onClick={() => router.push(`/admin/users/${u.id}`)}>
                        <Eye className="h-4 w-4" aria-hidden="true" />
                      </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          aria-label={`View wallet for user ${u.id}`}
                          onClick={() => openWallet(u.id)}
                        >
                          <Wallet className="h-4 w-4" aria-hidden="true" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          aria-label={`Impersonate user ${u.id}`}
                          onClick={() => handleImpersonate(u.id)}
                        >
                          <LogIn className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Dialog open={!!selectedUserId} onOpenChange={closeWallet}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>User Wallet</DialogTitle>
            <DialogDescription>
              Wallet balance and payment history for user #{selectedUserId}
            </DialogDescription>
          </DialogHeader>
          {walletLoading ? (
            <p className="py-4 text-center text-muted-foreground">Loading wallet...</p>
          ) : wallet ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Balance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{wallet.balance_rub} &#8381;</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Bonus Balance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{wallet.bonus_balance} &#8381;</p>
                  </CardContent>
                </Card>
              </div>
              <p className="text-xs text-muted-foreground">
                Last updated: {wallet.updated_at ? new Date(wallet.updated_at).toLocaleString() : "—"}
              </p>
              <Card>
                <CardHeader>
                  <CardTitle>Payment History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" aria-label="Payment history">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-3 font-medium">ID</th>
                          <th className="text-right py-2 px-3 font-medium">Amount</th>
                          <th className="text-left py-2 px-3 font-medium">Status</th>
                          <th className="text-left py-2 px-3 font-medium">Method</th>
                          <th className="text-left py-2 px-3 font-medium">Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {payments.map((p) => (
                          <tr key={p.id} className="border-b last:border-0">
                            <td className="py-2 px-3 font-mono">#{p.id}</td>
                            <td className="py-2 px-3 text-right">{p.amount_rub} &#8381;</td>
                            <td className="py-2 px-3">{p.status}</td>
                            <td className="py-2 px-3">{p.method}</td>
                            <td className="py-2 px-3">{new Date(p.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {payments.length === 0 && (
                      <p className="py-4 text-center text-muted-foreground">No payments found.</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p className="py-4 text-center text-muted-foreground">No wallet found for this user.</p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
