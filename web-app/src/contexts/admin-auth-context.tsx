"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import { apiFetch, clearAuthTokens, getAccessToken } from "@/lib/api"
import type { AdminUser } from "@/types/admin"

interface AdminAuthContextValue {
  user: AdminUser | null
  loading: boolean
  error: string | null
  checkAdmin: () => Promise<void>
  logout: () => void
}

const AdminAuthContext = createContext<AdminAuthContextValue | null>(null)

export function AdminAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AdminUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const checkAdmin = useCallback(async () => {
    setLoading(true)
    setError(null)
    const token = getAccessToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const u = await apiFetch<AdminUser>("/auth/me")
      if (!u.is_admin) {
        setError("Admin access required")
        setUser(null)
      } else {
        setUser(u)
      }
    } catch (err: unknown) {
      setError((err as Error)?.message || "Auth check failed")
      setUser(null)
      clearAuthTokens()
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAdmin()
  }, [checkAdmin])

  const handleLogout = useCallback(() => {
    clearAuthTokens()
    setUser(null)
  }, [])

  return (
    <AdminAuthContext.Provider value={{ user, loading, error, checkAdmin, logout: handleLogout }}>
      {children}
    </AdminAuthContext.Provider>
  )
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext)
  if (!ctx) throw new Error("useAdminAuth must be used within AdminAuthProvider")
  return ctx
}
