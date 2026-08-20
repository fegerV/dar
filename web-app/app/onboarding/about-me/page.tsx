"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { User } from "lucide-react"
import { OptionCard } from "@/components/option-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { useAppStore } from "@/store/app-store"

type Gender = "male" | "female" | "teen" | "other" | "prefer_not"

export default function AboutMePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { setUser } = useAppStore()
  const [gender, setGender] = useState<Gender | null>(null)
  const [age, setAge] = useState("")
  const [ageError, setAgeError] = useState(false)

  const genders: { value: Gender; label: string; description: string }[] = [
    { value: "male", label: "onboarding.about_me.male", description: "onboarding.about_me.male" },
    { value: "female", label: "onboarding.about_me.female", description: "onboarding.about_me.female" },
    { value: "teen", label: "onboarding.about_me.teen", description: "onboarding.about_me.teen" },
    { value: "other", label: "onboarding.about_me.other", description: "onboarding.about_me.other" },
    { value: "prefer_not", label: "onboarding.about_me.prefer_not", description: "onboarding.about_me.prefer_not" },
  ]

  const validateAge = (value: string): boolean => {
    if (!value) return true
    const num = Number(value)
    return num >= 1 && num <= 120
  }

  const handleAgeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setAge(value)
    if (value && !validateAge(value)) {
      setAgeError(true)
    } else {
      setAgeError(false)
    }
  }

  const handleNext = () => {
    if (age && !validateAge(age)) {
      setAgeError(true)
      return
    }
    const selectedGender = gender === "prefer_not" ? undefined : gender
    setUser({ gender: selectedGender, age: age ? Number(age) : undefined })
    router.push("/onboarding/photos")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Progress value={25} aria-label="Step 1 of 4" className="h-2 mb-2" />
          <p className="text-sm text-muted-foreground text-center">Шаг 1 из 4</p>
        </div>

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
              onChange={handleAgeChange}
              min={1}
              max={120}
              aria-invalid={ageError}
              aria-describedby={ageError ? "age-error" : undefined}
            />
            {ageError && (
              <p id="age-error" className="text-sm text-destructive">
                {t("onboarding.about_me.age_error")}
              </p>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("onboarding.about_me.back")}
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
