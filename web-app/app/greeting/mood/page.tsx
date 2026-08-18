"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { OptionCard } from "@/components/option-card"
import { useAppStore } from "@/store/app-store"

const moods: { value: "tears" | "laugh" | "wow" | "stylish" | "cinematic" | "unusual"; title: string; description: string }[] = [
  { value: "tears", title: "greeting.mood.tears", description: "Напряжённые моменты с эмоциональным подъёмом" },
  { value: "laugh", title: "greeting.mood.laugh", description: "Юмор и лёгкость" },
  { value: "wow", title: "greeting.mood.wow", description: "Эффектно и сюрприз" },
  { value: "stylish", title: "greeting.mood.stylish", description: "Красиво и минималистично" },
  { value: "cinematic", title: "greeting.mood.cinematic", description: "Как в кино" },
  { value: "unusual", title: "greeting.mood.unusual", description: "Нестандартно и креативно" },
]

export default function GreetingMoodPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting } = useAppStore()
  const [selectedMood, setSelectedMood] = useState<string | null>(null)

  const handleNext = () => {
    if (selectedMood) {
      updateCurrentGreeting({ mood: selectedMood as any })
      router.push("/greeting/concepts")
    }
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.mood.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.mood.subtitle")}</p>

        <div className="grid grid-cols-2 gap-3">
          {moods.map((mood) => (
            <OptionCard
              key={mood.value}
              title={mood.title}
              description={mood.description}
              selected={selectedMood === mood.value}
              onClick={() => setSelectedMood(mood.value)}
            />
          ))}
        </div>

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} className="flex-1">
            {t("common.back")}
          </Button>
          <Button onClick={handleNext} disabled={!selectedMood} className="flex-1">
            {t("greeting.mood.next")}
          </Button>
        </div>
      </div>
    </div>
  )
}
