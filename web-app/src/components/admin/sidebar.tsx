"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import { LayoutDashboard, ShoppingCart, Sparkles, GitBranch, Users, FileText, CreditCard, Bot, Settings } from "lucide-react"

const navItems = [
  { href: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/orders", label: "Orders", icon: ShoppingCart },
  { href: "/admin/generations", label: "Generations", icon: Sparkles },
  { href: "/admin/queue", label: "Queue", icon: GitBranch },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/templates", label: "Templates", icon: FileText },
  { href: "/admin/payments", label: "Payments", icon: CreditCard },
  { href: "/admin/workers", label: "AI / Workers", icon: Bot },
  { href: "/admin/system", label: "System", icon: Settings },
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r bg-background min-h-screen">
      <div className="p-4 border-b">
        <Link href="/admin/dashboard" className="flex items-center space-x-2 font-bold text-lg">
          <Sparkles className="h-5 w-5" aria-hidden="true" />
          <span>DarAgent Admin</span>
        </Link>
      </div>
      <nav className="p-2 space-y-1" aria-label="Admin">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                isActive ? "bg-primary text-primary-foreground" : "hover:bg-accent hover:text-accent-foreground"
              }`}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
