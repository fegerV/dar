"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function WelcomePage() {
  const { t } = useTranslation()
  const router = useRouter()

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4 py-12">
      <div className="flex flex-col items-center space-y-6 text-center max-w-md">
        <Sparkles className="h-16 w-16 text-primary" />
        <h1 className="text-3xl font-bold">{t("welcome.title")}</h1>
        <p className="text-muted-foreground">
          Создавайте персонализированные видеопоздравления с помощью AI
        </p>
        <div className="flex flex-col gap-3 w-full">
          <Button size="lg" className="w-full" onClick={() => router.push("/auth")}>
            {t("welcome.start")}
          </Button>
          <Button variant="outline" size="lg" className="w-full" onClick={() => router.push("/auth")}>
            {t("welcome.have_account")}
          </Button>
        </div>
      </div>
    </div>
  )
}
