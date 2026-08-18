"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { User } from "lucide-react"
import { OptionCard } from "@/components/option-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAppStore } from "@/store/app-store"

type Gender = "male" | "female" | "teen" | "other"

export default function AboutMePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { setUser } = useAppStore()
  const [gender, setGender] = useState<Gender | null>(null)
  const [age, setAge] = useState("")

  const genders: { value: Gender; label: string; description: string }[] = [
    { value: "male", label: "onboarding.about_me.male", description: "onboarding.about_me.male" },
    { value: "female", label: "onboarding.about_me.female", description: "onboarding.about_me.female" },
    { value: "teen", label: "onboarding.about_me.teen", description: "onboarding.about_me.teen" },
    { value: "other", label: "onboarding.about_me.other", description: "onboarding.about_me.other" },
  ]

  const handleNext = () => {
    setUser({ gender: gender || undefined, age: age ? Number(age) : undefined })
    router.push("/onboarding/photos")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          ← {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("onboarding.about_me.title")}</h1>
        <p className="text-muted-foreground mb-6">Расскажите немного о себе</p>

        <div className="space-y-6">
          <div className="space-y-3">
            <Label>{t("onboarding.about_me.gender_label")}</Label>
            <div className="grid grid-cols-2 gap-3">
              {genders.map((g) => (
                <OptionCard
                  key={g.value}
                  title={g.label}
                  description={g.description}
                  selected={gender === g.value}
                  onClick={() => setGender(g.value)}
                />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="age">{t("onboarding.about_me.age_label")}</Label>
            <Input
              id="age"
              type="number"
              placeholder={t("onboarding.about_me.age_placeholder")}
              value={age}
              onChange={(e) => setAge(e.target.value)}
              min={1}
              max={120}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleNext} className="flex-1">
              {t("onboarding.about_me.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
