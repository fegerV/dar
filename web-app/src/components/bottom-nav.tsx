"use client"

import { usePathname, useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Home, History, Image, User } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/home", label: "home.title", icon: Home },
  { href: "/photos", label: "photos.title", icon: Image },
  { href: "/history", label: "history.title", icon: History },
  { href: "/profile", label: "profile.title", icon: User },
]

export function BottomNav() {
  const pathname = usePathname()
  const { t } = useTranslation()
  const router = useRouter()

  const isGreetingFlow = pathname?.startsWith("/greeting")
  const isAdminPage = pathname?.startsWith("/admin")
  if (isGreetingFlow || isAdminPage) return null

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:hidden">
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex items-center justify-around h-14">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <button
                key={item.href}
                onClick={() => router.push(item.href)}
                className={cn(
                  "flex flex-col items-center justify-center gap-0.5 py-2 px-3 rounded-md transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
                aria-label={t(item.label)}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon className="h-5 w-5" aria-hidden="true" />
                <span className="text-[10px] font-medium">{t(item.label)}</span>
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
