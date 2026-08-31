"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useAppStore } from "@/store/app-store"

export default function GreetingReviewPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state } = useAppStore()
  const greeting = state.currentGreeting

  if (!greeting) {
    router.push("/greeting/new")
    return null
  }

  const handleGenerate = () => {
    router.push("/greeting/payment")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.review.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.review.subtitle")}</p>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Получатель</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-medium">{greeting.recipientName || "Не указано"}</p>
              <p className="text-sm text-muted-foreground">
                {greeting.recipientAge ? `${greeting.recipientAge} лет` : ""}
                {greeting.relationship ? `, ${greeting.relationship}` : ""}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Повод</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge>{t(`greeting.occasion.${greeting.occasion}`)}</Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Настроение</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">{t(`greeting.mood.${greeting.mood}`)}</Badge>
            </CardContent>
          </Card>

          {greeting.greetingText && (
            <Card>
              <CardHeader>
                <CardTitle>Текст</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{greeting.greetingText.text}</p>
              </CardContent>
            </Card>
          )}

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleGenerate} className="flex-1">
              {t("greeting.review.generate")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
