"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { BottomNav } from "@/components/bottom-nav"
import { useAppStore } from "@/store/app-store"

export default function HomePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state } = useAppStore()

  const recentGreetings = state.history.slice(-3).reverse()

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">{t("home.title")}</h1>
            <p className="text-muted-foreground mt-1">Создавайте поздравления с AI</p>
          </div>
          <Button onClick={() => router.push("/greeting/new")} size="lg">
            <Sparkles className="h-4 w-4 mr-2" />
            {t("home.new_greeting")}
          </Button>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-4">Последние поздравления</h2>
            {recentGreetings.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground">{t("home.no_greetings")}</p>
                  <p className="text-sm text-muted-foreground mt-1">{t("home.no_greetings_subtitle")}</p>
                  <Button className="mt-4" onClick={() => router.push("/greeting/new")}>
                    {t("home.new_greeting")}
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {recentGreetings.map((greeting) => (
                  <Card key={greeting.id} className="cursor-pointer hover:border-primary/50" onClick={() => router.push(`/greeting/result?id=${greeting.id}`)}>
                    <CardHeader>
                      <CardTitle className="text-lg">{greeting.recipientName || "Поздравление"}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-3">
                        {t(`greeting.occasion.${greeting.occasion}`)}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          greeting.status === "completed" ? "bg-green-100 text-green-800" :
                          greeting.status === "generating" ? "bg-blue-100 text-blue-800" :
                          "bg-gray-100 text-gray-800"
                        }`}>
                          {greeting.status === "completed" ? "Завершено" :
                           greeting.status === "generating" ? "Генерация..." : "Черновик"}
                        </span>
                        <Button variant="ghost" size="sm">{t("home.view_details")}</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <BottomNav />
    </div>
  )
}
