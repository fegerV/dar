"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import type { AdminRole, SystemRoleDef } from "@/types/admin"

interface PermissionsResponse {
  roles: Record<string, SystemRoleDef>
  permissions: string[]
}

export function AdminRBAC() {
  const [roles, setRoles] = useState<AdminRole[]>([])
  const [allPermissions, setAllPermissions] = useState<string[]>([])
  const [systemRoles, setSystemRoles] = useState<Record<string, SystemRoleDef>>({})
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ code: "", name: "", description: "", permissions: [] as string[] })
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) router.push("/admin/login")
  }, [authLoading, user, router])

  const loadRoles = async () => {
    setLoading(true)
    try {
      const [rolesData, permsData] = await Promise.all([
        apiFetch<AdminRole[]>("/admin/roles"),
        apiFetch<PermissionsResponse>("/admin/rbac/permissions"),
      ])
      setRoles(rolesData)
      setAllPermissions(permsData.permissions)
      setSystemRoles(permsData.roles)
    } catch {
      setRoles([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadRoles()
  }, [user])

  const createRole = async () => {
    if (!form.code || !form.name) return
    try {
      await apiFetch<AdminRole>("/admin/roles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      setCreating(false)
      setForm({ code: "", name: "", description: "", permissions: [] })
      loadRoles()
    } catch (e: unknown) {
      alert((e as Error)?.message || "Failed to create role")
    }
  }

  if (authLoading || loading) {
    return <p className="text-center py-8">Loading roles...</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">RBAC Management</h1>
          <p className="text-muted-foreground mt-1">Manage roles and permissions</p>
        </div>
        <Button onClick={() => setCreating(!creating)} variant={creating ? "secondary" : "default"}>
          {creating ? "Cancel" : "New Role"}
        </Button>
      </div>

      {creating && (
        <Card>
          <CardHeader><CardTitle>Create Role</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><Label>Code</Label><Input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} aria-label="Role code" /></div>
            <div><Label>Name</Label><Input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} aria-label="Role name" /></div>
            <div><Label>Description</Label><Textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} aria-label="Role description" /></div>
            <Button onClick={createRole}>Create Role</Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>System Roles</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Object.entries(systemRoles).map(([code, def]) => (
              <div key={code} className="border rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <strong>{code}</strong> — <Badge variant="secondary">{def.permissions.length} permissions</Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">{def.permissions.join(", ")}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Custom Roles</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Code</th><th className="text-left py-2">Name</th><th className="text-left py-2">Permissions</th><th className="text-right py-2">System</th></tr></thead>
            <tbody>
              {roles.map((role) => (
                <tr key={role.id} className="border-b">
                  <td className="py-2 font-mono">{role.code}</td>
                  <td className="py-2">{role.name}</td>
                  <td className="py-2">{role.permissions.join(", ") || "—"}</td>
                  <td className="py-2 text-right">{role.is_system ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
