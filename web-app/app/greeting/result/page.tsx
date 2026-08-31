"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, Play, Share2, Star, PlusCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useAppStore } from "@/store/app-store"

export default function GreetingResultPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, completeCurrentGreeting } = useAppStore()
  const greeting = state.currentGreeting

  if (!greeting) {
    router.push("/home")
    return null
  }

  const handlePlay = () => {
    alert("Плейер видео (mock)")
  }

  const handleShare = () => {
    router.push("/greeting/share")
  }

  const handleRate = () => {
    router.push("/greeting/rating")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.result.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.result.subtitle")}</p>

        <Card className="mb-6">
          <CardContent className="py-12 flex flex-col items-center justify-center">
            <div className="w-full aspect-video bg-muted rounded-lg flex items-center justify-center mb-4">
              <div className="text-center">
                <Play className="h-16 w-16 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Видео готово</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-3">
          <Button onClick={handlePlay} className="w-full flex items-center gap-2">
            <Play className="h-4 w-4" />
            {t("greeting.result.play")}
          </Button>
          <Button variant="outline" onClick={handleShare} className="w-full flex items-center gap-2">
            <Share2 className="h-4 w-4" />
            {t("greeting.result.share")}
          </Button>
          <Button variant="secondary" onClick={handleRate} className="w-full flex items-center gap-2">
            <Star className="h-4 w-4" />
            {t("greeting.result.rate")}
          </Button>
        </div>

        <Button
          variant="outline"
          className="w-full mt-6"
          onClick={() => {
            completeCurrentGreeting()
            router.push("/greeting/new")
          }}
        >
          <PlusCircle className="h-4 w-4 mr-2" />
          {t("greeting.result.new_greeting")}
        </Button>
      </div>
    </div>
  )
}
