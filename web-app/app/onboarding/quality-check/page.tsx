"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { MockGenerator } from "@/components/mock-generator"
import { useAppStore } from "@/store/app-store"

export default function QualityCheckPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, setUser } = useAppStore()
  const [bestIndex, setBestIndex] = useState<number | null>(null)

  const handleAutoSelect = (index: number) => {
    setBestIndex(index)
  }

  const handleNext = () => {
    setUser({ isOnboarded: true })
    router.push("/home")
  }

  if (state.user.photos.length === 0) {
    router.push("/onboarding/photos")
    return null
  }

  const isLowQuality = bestIndex !== null && state.user.photos.length > 0

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Progress value={75} aria-label="Step 3 of 4" className="h-2 mb-2" />
          <p className="text-sm text-muted-foreground text-center">Шаг 3 из 4</p>
        </div>

        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          ← {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("onboarding.quality_check.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("onboarding.quality_check.subtitle")}</p>

        <MockGenerator photos={state.user.photos} onComplete={handleAutoSelect} />

        {bestIndex !== null && (
          <div className="mt-6 p-4 rounded-lg border border-primary bg-primary/5">
            <p className="text-sm font-medium mb-2">Выбрано фото #{bestIndex + 1}</p>
            <img
              src={state.user.photos[bestIndex]}
              alt="Best photo"
              className="w-32 h-32 object-cover rounded-lg mx-auto"
            />
            {isLowQuality && (
              <p className="text-xs text-warning mt-2">{t("onboarding.quality_check.low_quality")}</p>
            )}
            <Button onClick={handleNext} className="w-full mt-4">
              {t("onboarding.quality_check.next")}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
