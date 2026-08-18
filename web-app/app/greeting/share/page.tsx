"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, Share2, MessageCircle, Send, Link2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { useAppStore } from "@/store/app-store"

export default function GreetingSharePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state } = useAppStore()

  const shareUrl = `https://daragent.ru/greeting/${state.currentGreeting?.id || "demo"}`

  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl)
    alert("Ссылка скопирована")
  }

  const shareWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(shareUrl)}`, "_blank")
  }

  const shareTelegram = () => {
    window.open(`https://t.me/share/url?url=${encodeURIComponent(shareUrl)}`, "_blank")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("greeting.share.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.share.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.share.subtitle")}</p>

        <div className="grid grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:border-primary/50" onClick={copyLink}>
            <CardContent className="py-8 flex flex-col items-center gap-3">
              <Link2 className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">{t("greeting.share.copy_link")}</span>
            </CardContent>
          </Card>
          <Card className="cursor-pointer hover:border-primary/50" onClick={shareWhatsApp}>
            <CardContent className="py-8 flex flex-col items-center gap-3">
              <MessageCircle className="h-8 w-8 text-green-500" />
              <span className="text-sm font-medium">{t("greeting.share.whatsapp")}</span>
            </CardContent>
          </Card>
          <Card className="cursor-pointer hover:border-primary/50" onClick={shareTelegram}>
            <CardContent className="py-8 flex flex-col items-center gap-3">
              <Send className="h-8 w-8 text-blue-500" />
              <span className="text-sm font-medium">{t("greeting.share.telegram")}</span>
            </CardContent>
          </Card>
        </div>

        <div className="mt-6 p-4 rounded-lg border bg-muted/50">
          <p className="text-xs text-muted-foreground mb-2">Ссылка на поздравление:</p>
          <p className="text-sm font-mono break-all">{shareUrl}</p>
        </div>
      </div>
    </div>
  )
}
