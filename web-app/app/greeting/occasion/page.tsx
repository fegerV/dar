"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, Cake, Gift, Heart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { OptionCard } from "@/components/option-card"
import { useAppStore } from "@/store/app-store"

const occasions: { value: "birthday" | "new_year" | "march_8" | "february_23" | "wedding" | "anniversary" | "graduation" | "defender_day" | "custom"; title: string; description: string; icon: React.ReactNode }[] = [
  { value: "birthday", title: "День рождения", description: "birthday", icon: <Cake className="h-6 w-6 text-primary" /> },
  { value: "new_year", title: "Новый год", description: "new_year", icon: <Gift className="h-6 w-6 text-primary" /> },
  { value: "march_8", title: "8 марта", description: "march_8", icon: <Heart className="h-6 w-6 text-primary" /> },
  { value: "february_23", title: "23 февраля", description: "february_23", icon: <Gift className="h-6 w-6 text-primary" /> },
  { value: "wedding", title: "Свадьба", description: "wedding", icon: <Heart className="h-6 w-6 text-primary" /> },
  { value: "anniversary", title: "Юбилей", description: "anniversary", icon: <Cake className="h-6 w-6 text-primary" /> },
  { value: "graduation", title: "Выпускной", description: "graduation", icon: <Gift className="h-6 w-6 text-primary" /> },
  { value: "defender_day", title: "День защитника", description: "defender_day", icon: <Heart className="h-6 w-6 text-primary" /> },
  { value: "custom", title: "Другое", description: "custom", icon: <Gift className="h-6 w-6 text-primary" /> },
]

export default function GreetingOccasionPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting } = useAppStore()
  const [selected, setSelected] = useState<string | null>(null)

  const handleNext = () => {
    if (selected) {
      updateCurrentGreeting({ occasion: selected as "birthday" | "new_year" | "march_8" | "february_23" | "wedding" | "anniversary" | "graduation" | "defender_day" | "custom" })
      router.push("/greeting/relationship")
    }
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.occasion.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.occasion.subtitle")}</p>

        <div className="grid grid-cols-2 gap-3">
          {occasions.map((occ) => (
            <OptionCard
              key={occ.value}
              title={occ.title}
              description={occ.description}
              icon={occ.icon}
              selected={selected === occ.value}
              onClick={() => setSelected(occ.value)}
            />
          ))}
        </div>

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} className="flex-1">
            {t("common.back")}
          </Button>
          <Button onClick={handleNext} disabled={!selected} className="flex-1">
            {t("common.next")}
          </Button>
        </div>
      </div>
    </div>
  )
}
