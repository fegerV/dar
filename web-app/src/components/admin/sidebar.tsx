"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import { LayoutDashboard, ShoppingCart, Sparkles, GitBranch, Users, FileText, Edit3, CreditCard, Bot, Settings, ClipboardList, Shield, ShieldCheck, AlertCircle, Percent, BarChart3, LifeBuoy, HardDrive, Webhook } from "lucide-react"
import { useTranslation } from "react-i18next"

interface NavItem {
  href: string
  i18nKey: string
  icon: React.ElementType
}

const navItems: NavItem[] = [
  { href: "/admin/dashboard", i18nKey: "admin.sidebar.dashboard", icon: LayoutDashboard },
  { href: "/admin/orders", i18nKey: "admin.sidebar.orders", icon: ShoppingCart },
  { href: "/admin/generations", i18nKey: "admin.sidebar.generations", icon: Sparkles },
  { href: "/admin/errors", i18nKey: "admin.sidebar.errors", icon: AlertCircle },
  { href: "/admin/queue", i18nKey: "admin.sidebar.queue", icon: GitBranch },
  { href: "/admin/users", i18nKey: "admin.sidebar.users", icon: Users },
  { href: "/admin/support", i18nKey: "admin.sidebar.support", icon: LifeBuoy },
  { href: "/admin/moderation", i18nKey: "admin.sidebar.moderation", icon: Gavel },
  { href: "/admin/templates", i18nKey: "admin.sidebar.templates", icon: FileText },
  { href: "/admin/prompts", i18nKey: "admin.sidebar.prompts", icon: Edit3 },
  { href: "/admin/ai", i18nKey: "admin.sidebar.ai_models", icon: Bot },
  { href: "/admin/workers", i18nKey: "admin.sidebar.workers", icon: Bot },
  { href: "/admin/rbac", i18nKey: "admin.sidebar.rbac", icon: ShieldCheck },
  { href: "/admin/promo", i18nKey: "admin.sidebar.promo", icon: Percent },
  { href: "/admin/analytics", i18nKey: "admin.sidebar.analytics", icon: BarChart3 },
  { href: "/admin/storage", i18nKey: "admin.sidebar.storage", icon: HardDrive },
  { href: "/admin/webhooks", i18nKey: "admin.sidebar.webhooks", icon: Webhook },
  { href: "/admin/payments", i18nKey: "admin.sidebar.payments", icon: CreditCard },
  { href: "/admin/ledger", i18nKey: "admin.sidebar.ledger", icon: BarChart3 },
  { href: "/admin/referrals", i18nKey: "admin.sidebar.referrals", icon: ClipboardList },
  { href: "/admin/audit-logs", i18nKey: "admin.sidebar.audit_logs", icon: Shield },
  { href: "/admin/system", i18nKey: "admin.sidebar.system", icon: Settings },
  { href: "/admin/help", i18nKey: "admin.sidebar.help", icon: LifeBuoy },
]

export function AdminSidebar() {
  const { t } = useTranslation()
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r bg-background min-h-screen">
      <div className="p-4 border-b">
        <Link href="/admin/dashboard" className="flex items-center space-x-2 font-bold text-lg">
          <Sparkles className="h-5 w-5" aria-hidden="true" />
          <span>DarAgent Admin</span>
        </Link>
      </div>
      <nav className="p-2 space-y-1" aria-label="Admin navigation">
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
              <span>{t(item.i18nKey)}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
