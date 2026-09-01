"use client"

import { AdminSidebar } from "@/components/admin/sidebar"
import { AdminAuthProvider, useAdminAuth } from "@/contexts/admin-auth-context"
import { Moon, Sun, User } from "lucide-react"
import { useTheme } from "next-themes"
import { usePathname } from "next/navigation"

function AdminHeader() {
  const { user, logout } = useAdminAuth()
  const { theme, setTheme } = useTheme()

  return (
    <header className="border-b bg-background/80 backdrop-blur">
      <div className="flex h-14 items-center justify-end gap-4 px-4">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="rounded-md p-2 hover:bg-accent"
          aria-label="Toggle theme"
          title="Toggle theme"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" aria-hidden="true" /> : <Moon className="h-4 w-4" aria-hidden="true" />}
        </button>
        {user && (
          <div className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4" aria-hidden="true" />
            <span>{user.display_name || user.email || "Admin"}</span>
            <button onClick={logout} className="text-sm underline" aria-label="Logout">Logout</button>
          </div>
        )}
      </div>
    </header>
  )
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const isLoginPage = pathname === "/admin/login"

  if (isLoginPage) {
    return (
      <AdminAuthProvider>
        <div className="min-h-screen bg-muted/30">
          {children}
        </div>
      </AdminAuthProvider>
    )
  }

  return (
    <AdminAuthProvider>
      <div className="min-h-screen bg-muted/30">
        <div className="flex">
          <AdminSidebar />
          <main className="flex-1 flex flex-col">
            <AdminHeader />
            <div className="flex-1 p-6 lg:p-8">
              <div className="mx-auto max-w-7xl">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </AdminAuthProvider>
  )
}
