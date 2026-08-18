"use client"

import { ThemeProvider } from "next-themes"
import { SessionProvider } from "next-auth/react"
import { I18nextProvider } from "react-i18next"
import i18n from "@/i18n"
import { AppStoreProvider } from "@/store/app-store"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <SessionProvider>
          <AppStoreProvider>
            {children}
          </AppStoreProvider>
        </SessionProvider>
      </ThemeProvider>
    </I18nextProvider>
  )
}
