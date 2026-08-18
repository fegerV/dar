"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAppStore } from "@/store/app-store"

export default function GreetingRecipientPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting, addRecipient } = useAppStore()
  const [name, setName] = useState("")
  const [age, setAge] = useState("")
  const [nickname, setNickname] = useState("")

  const handleNext = () => {
    const recipientData = { name, age: age ? Number(age) : undefined, nickname }
    updateCurrentGreeting({
      recipientName: name,
      recipientAge: age ? Number(age) : undefined,
    })
    addRecipient({
      id: Date.now().toString(),
      name,
      age: age ? Number(age) : undefined,
      nickname,
      interests: [],
      personality: [],
    })
    router.push("/greeting/occasion")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.recipient.title")}</h1>
        <p className="text-muted-foreground mb-6">Данные получателя</p>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">{t("greeting.recipient.name_label")}</Label>
            <Input
              id="name"
              placeholder={t("greeting.recipient.name_placeholder")}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age">{t("greeting.recipient.age_label")}</Label>
            <Input
              id="age"
              type="number"
              placeholder={t("greeting.recipient.age_placeholder")}
              value={age}
              onChange={(e) => setAge(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="nickname">{t("greeting.recipient.nickname_label")}</Label>
            <Input
              id="nickname"
              placeholder={t("greeting.recipient.nickname_placeholder")}
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleNext} disabled={!name.trim()} className="flex-1">
              {t("greeting.recipient.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
