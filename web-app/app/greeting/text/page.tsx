"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { useAppStore } from "@/store/app-store"

export default function GreetingTextPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting, state } = useAppStore()
  const [text, setText] = useState("")
  const [style, setStyle] = useState("formal")

  const handleRegenerate = () => {
    setText(`Дорогой ${state.currentGreeting?.recipientName || "друг"}! В этот особенный день мы хотим пожелать тебе счастья, здоровья и исполнения самых заветных желаний. Пусть каждый день приносит радость и новые возможности!`)
  }

  const handleNext = () => {
    updateCurrentGreeting({
      greetingText: { text, style, tone: style },
    })
    router.push("/greeting/template")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.text.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.text.subtitle")}</p>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="text">{t("greeting.text.title")}</Label>
            <Textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Введите текст поздравления..."
              rows={6}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="style">{t("greeting.text.style_label")}</Label>
            <Select value={style} onValueChange={setStyle}>
              <option value="formal">Официальный</option>
              <option value="informal">Неформальный</option>
              <option value="funny">Юмористический</option>
              <option value="emotional">Эмоциональный</option>
              <option value="poetic">Поэтический</option>
              <option value="short">Короткий</option>
            </Select>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={handleRegenerate} className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              {t("greeting.text.regenerate")}
            </Button>
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleNext} disabled={!text.trim()} className="flex-1">
              {t("greeting.text.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
