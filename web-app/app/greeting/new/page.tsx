"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Users, UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { OptionCard } from "@/components/option-card"
import { useAppStore } from "@/store/app-store"

export default function GreetingNewPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, setCurrentGreeting } = useAppStore()

  const handleStart = () => {
    setCurrentGreeting({
      id: Date.now().toString(),
      occasion: "birthday",
      mood: "wow",
      concepts: [],
      status: "draft",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    })
    router.push("/greeting/who")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-bold mb-6">{t("greeting.who.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.who.subtitle")}</p>

        <div className="space-y-4">
          <OptionCard
            title="greeting.who.select_existing"
            description="Выберите из сохранённых получателей"
            icon={<Users className="h-6 w-6 text-primary" />}
            onClick={() => state.recipients.length > 0 && router.push("/greeting/who")}
          />
          <OptionCard
            title="greeting.who.create_new"
            description="Создайте нового получателя"
            icon={<UserPlus className="h-6 w-6 text-primary" />}
            onClick={handleStart}
          />
        </div>
      </div>
    </div>
  )
}
