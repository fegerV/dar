"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Calendar, Plus, Save, X } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useRouter } from "next/navigation"

interface PromoCode {
  id: string
  code: string
  discount_type: string
  discount_value: number
  max_uses: number | null
  used_count: number
  expires_at: string | null
  is_active: boolean
  created_at: string
}

export function AdminPromoCodes() {
  const [promos, setPromos] = useState<PromoCode[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<PromoCode | null>(null)
  const [draft, setDraft] = useState<Partial<PromoCode>>({})
  const [saving, setSaving] = useState(false)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadPromos = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<PromoCode[]>("/admin/promo-codes")
      setPromos(data)
    } catch {
      setPromos([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadPromos()
  }, [user])

  const startEdit = (promo: PromoCode | null) => {
    setEditing(promo)
    setDraft(promo || { code: "", discount_type: "fixed", discount_value: 0, is_active: true })
  }

  const save = async () => {
    if (!draft.code || !draft.discount_type || !draft.discount_value) {
      alert("Code, type, and value are required")
      return
    }
    setSaving(true)
    try {
      if (editing) {
        await apiFetch<PromoCode>(`/admin/promo-codes/${editing.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            discount_value: draft.discount_value,
            max_uses: draft.max_uses,
            expires_at: draft.expires_at ? new Date(draft.expires_at).toISOString() : null,
            is_active: draft.is_active,
          }),
        })
      } else {
        await apiFetch<PromoCode>("/admin/promo-codes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            code: draft.code,
            discount_type: draft.discount_type,
            discount_value: draft.discount_value,
            max_uses: draft.max_uses,
            expires_at: draft.expires_at ? new Date(draft.expires_at).toISOString() : null,
            is_active: draft.is_active,
          }),
        })
      }
      setEditing(null)
      setDraft({})
      loadPromos()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Save failed")
    } finally {
      setSaving(false)
    }
  }

  const deletePromo = async (id: string) => {
    if (!confirm("Delete this promo code?")) return
    try {
      await apiFetch(`/admin/promo-codes/${id}`, { method: "DELETE" })
      setPromos(promos.filter(p => p.id !== id))
    } catch (e: unknown) {
      alert((e as Error)?.message || "Delete failed")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading promo codes...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold">Promo Codes</h1><p className="text-muted-foreground mt-1">Create and manage promotional codes</p></div>
        <Button onClick={() => startEdit(null)}>
          <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
          New Promo Code
        </Button>
      </div>

      {editing !== null && (
        <Card>
          <CardHeader><CardTitle>{editing.id ? "Edit Promo Code" : "New Promo Code"}</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Code</Label><Input value={draft.code || ""} onChange={e => setDraft({ ...draft, code: e.target.value })} aria-label="Code" /></div>
              <div><Label>Type</Label>
                <select value={draft.discount_type || "fixed"} onChange={e => setDraft({ ...draft, discount_type: e.target.value })} className="w-full border rounded px-2 py-1" aria-label="Discount type">
                  <option value="fixed">Fixed</option>
                  <option value="percentage">Percentage</option>
                  <option value="bonus">Bonus</option>
                  <option value="free">Free</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Value</Label><Input type="number" value={draft.discount_value || 0} onChange={e => setDraft({ ...draft, discount_value: parseFloat(e.target.value) })} aria-label="Discount value" /></div>
              <div><Label>Max Uses (empty = unlimited)</Label><Input type="number" value={draft.max_uses ?? ""} onChange={e => setDraft({ ...draft, max_uses: e.target.value ? parseInt(e.target.value) : null })} aria-label="Max uses" /></div>
            </div>
            <div><Label>Expires At</Label><Input type="datetime-local" value={draft.expires_at ? new Date(draft.expires_at).toISOString().slice(0, 16) : ""} onChange={e => setDraft({ ...draft, expires_at: e.target.value })} aria-label="Expires at" /></div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="is_active" checked={draft.is_active ?? true} onChange={e => setDraft({ ...draft, is_active: e.target.checked })} aria-label="Active" />
              <Label htmlFor="is_active">Active</Label>
            </div>
            <div className="flex gap-2">
              <Button onClick={save} disabled={saving}>{saving ? "Saving..." : (<><Save className="h-4 w-4 mr-2" aria-hidden="true" />Save</>)}</Button>
              <Button variant="ghost" onClick={() => { setEditing(null); setDraft({}) }}><X className="h-4 w-4" aria-hidden="true" /></Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Promo Codes ({promos.length})</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Code</th><th className="text-left py-2">Type</th><th className="text-left py-2">Value</th><th className="text-center py-2">Used</th><th className="text-center py-2">Status</th><th className="text-center py-2">Expires</th><th className="text-right py-2">Actions</th></tr></thead>
            <tbody>
              {promos.map((promo) => (
                <tr key={promo.id} className="border-b">
                  <td className="py-2 font-mono">{promo.code}</td>
                  <td className="py-2">{promo.discount_type}</td>
                  <td className="py-2">{promo.discount_value}</td>
                  <td className="py-2 text-center">{promo.used_count}{promo.max_uses ? `/${promo.max_uses}` : ""}</td>
                  <td className="py-2 text-center">
                    <Badge variant={promo.is_active ? "default" : "secondary"}>{promo.is_active ? "Active" : "Inactive"}</Badge>
                  </td>
                  <td className="py-2 text-center">{promo.expires_at ? new Date(promo.expires_at).toLocaleDateString() : "∞"}</td>
                  <td className="py-2 text-right">
                    <Button size="sm" variant="ghost" aria-label={`Edit promo ${promo.code}`} onClick={() => startEdit(promo)}>Edit</Button>
                    <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700" aria-label={`Delete promo ${promo.code}`} onClick={() => deletePromo(promo.id)}>Delete</Button>
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
