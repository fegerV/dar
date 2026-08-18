"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Home, PlusCircle, Sparkles, User } from "lucide-react"

const navItems = [
  { href: "/", label: "home", icon: Home },
  { href: "/dashboard", label: "dashboard", icon: Sparkles },
  { href: "/create", label: "new_greeting", icon: PlusCircle },
  { href: "/profile", label: "profile", icon: User },
]

export function Navbar() {
  const pathname = usePathname()
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2" aria-label="DarAgent Home">
            <Sparkles className="h-6 w-6" aria-hidden="true" />
            <span className="font-bold text-lg">DarAgent</span>
          </Link>

          <nav className="hidden md:flex items-center space-x-6" aria-label="Main">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-1 text-sm font-medium transition-colors ${
                    isActive ? "text-primary" : "text-muted-foreground hover:text-primary"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{t(item.label)}</span>
                </Link>
              )
            })}
          </nav>

          <nav className="md:hidden flex items-center space-x-4" aria-label="Mobile">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`p-2 rounded-md ${
                    isActive ? "text-primary bg-muted" : "text-muted-foreground"
                  }`}
                  aria-label={t(item.label)}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
