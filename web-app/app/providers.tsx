"use client"

import { Next13ReactProgressBar as ProgressBar } from "next13-react-progress-bar"
import { ThemeProvider } from "next-themes"
import { SessionProvider } from "next-auth/react"
import { I18nextProvider } from "react-i18next"
import i18n from "@/i18n"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <SessionProvider>
          {children}
          <ProgressBar height="2px" color="#000" options={{ showSpinner: false }} />
        </SessionProvider>
      </ThemeProvider>
    </I18nextProvider>
  )
}
