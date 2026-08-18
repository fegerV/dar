"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { apiFetch } from "@/lib/api"
import type { Referral, ReferralCode } from "@/types/admin"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"

const statusColors: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  failed: "bg-red-100 text-red-800",
}

export function AdminReferrals() {
  const [referrals, setReferrals] = useState<Referral[]>([])
  const [codes, setCodes] = useState<ReferralCode[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    Promise.all([
      apiFetch<Referral[]>("/admin/referrals").catch(() => []),
      apiFetch<ReferralCode[]>("/admin/referral-codes").catch(() => []),
    ]).then(([refs, cds]) => {
      setReferrals(refs)
      setCodes(cds)
      setLoading(false)
    })
  }, [user])

  if (authLoading || loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Referrals</h1>
          <p className="text-muted-foreground mt-1">Referral codes and conversions</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading referrals...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Referrals</h1>
        <p className="text-muted-foreground mt-1">Referral codes and conversions</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Referral Codes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Referral codes table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Code</th>
                  <th className="text-left py-3 px-4 font-medium">Owner</th>
                  <th className="text-center py-3 px-4 font-medium">Active</th>
                  <th className="text-center py-3 px-4 font-medium">Uses</th>
                  <th className="text-center py-3 px-4 font-medium">Max Uses</th>
                  <th className="text-left py-3 px-4 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {codes.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">{c.code}</td>
                    <td className="py-3 px-4">#{c.id}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={c.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                        {c.is_active ? "Yes" : "No"}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-center">{c.uses_count}</td>
                    <td className="py-3 px-4 text-center">{c.max_uses ?? "∞"}</td>
                    <td className="py-3 px-4">{new Date(c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {codes.length === 0 && (
              <p className="py-6 text-center text-muted-foreground">No referral codes found.</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Referrals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Referrals table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">Code</th>
                  <th className="text-left py-3 px-4 font-medium">Referrer</th>
                  <th className="text-left py-3 px-4 font-medium">Referred</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-center py-3 px-4 font-medium">Referrer Bonus</th>
                  <th className="text-center py-3 px-4 font-medium">Referee Bonus</th>
                  <th className="text-left py-3 px-4 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {referrals.map((r) => (
                  <tr key={r.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{r.id}</td>
                    <td className="py-3 px-4">{r.code}</td>
                    <td className="py-3 px-4">#{r.referrer_user_id}</td>
                    <td className="py-3 px-4">{r.referred_user_id ? `#${r.referred_user_id}` : "—"}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={statusColors[r.status] || "bg-gray-100"}>{r.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={r.referrer_bonus_granted ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                        {r.referrer_bonus_granted ? "Granted" : "Pending"}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={r.referee_bonus_granted ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                        {r.referee_bonus_granted ? "Granted" : "Pending"}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">{new Date(r.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {referrals.length === 0 && (
              <p className="py-6 text-center text-muted-foreground">No referrals found.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
