"use client"

import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { BottomNav } from "@/components/bottom-nav"
import { useAppStore } from "@/store/app-store"

export default function HistoryPage() {
  const { t } = useTranslation()
  const { state } = useAppStore()

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-6">{t("dashboard.title")}</h1>
        {state.history.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">История пуста</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {state.history.slice().reverse().map((greeting) => (
              <Card key={greeting.id}>
                <CardHeader>
                  <CardTitle>{greeting.recipientName || "Поздравление"}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {new Date(greeting.createdAt).toLocaleDateString("ru-RU")}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {t(`greeting.occasion.${greeting.occasion}`)}
                  </p>
                  {greeting.rating && (
                    <p className="text-sm mt-2">Оценка: {greeting.rating}/5</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
