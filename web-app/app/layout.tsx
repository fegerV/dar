import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Providers } from "./providers"
import { Navbar } from "@/components/navbar"

import "./globals.css"

const inter = Inter({ subsets: ["latin", "cyrillic"] })

export const metadata: Metadata = {
  title: "DarAgent — AI видеопоздравления",
  description: "Создавайте персонализированные видеопоздравления с помощью AI",
  manifest: "/manifest.json",
  themeColor: "#000000",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "DarAgent",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
            <Navbar />
            <main id="main-content" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}
