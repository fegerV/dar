"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Sparkles, Upload, FileVideo, CheckCircle2 } from "lucide-react"

const steps = [
  {
    titleKey: "onboarding.step1",
    description: "Загрузите фото получателя. Мы проверим качество и подберём лучшую модель.",
    icon: Upload,
  },
  {
    titleKey: "onboarding.step2",
    description: "Выберите сценарий из проверенных рецептов или создайте свой.",
    icon: Sparkles,
  },
  {
    titleKey: "onboarding.step3",
    description: "Получите готовое видео с автоматической проверкой качества.",
    icon: FileVideo,
  },
]

export function OnboardingScreen() {
  const { t } = useTranslation()
  const [currentStep, setCurrentStep] = useState(0)
  const [completed, setCompleted] = useState(false)

  const next = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep((s) => s + 1)
    } else {
      setCompleted(true)
    }
  }

  if (completed) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center">
        <CheckCircle2 className="h-16 w-16 text-green-600" aria-hidden="true" />
        <h1 className="text-2xl font-bold">{t("onboarding.title")}</h1>
        <p className="text-muted-foreground">{t("onboarding.subtitle")}</p>
        <Button asChild>
          <a href="/dashboard">{t("dashboard.title")}</a>
        </Button>
      </div>
    )
  }

  const step = steps[currentStep]
  const Icon = step.icon

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <div className="mb-8">
        <Progress value={((currentStep + 1) / steps.length) * 100} aria-label={`${currentStep + 1} of ${steps.length}`} />
      </div>

      <div className="flex flex-col items-center text-center space-y-6">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <Icon className="h-8 w-8 text-primary" aria-hidden="true" />
        </div>
        <h1 className="text-2xl font-bold">{t(step.titleKey)}</h1>
        <p className="text-muted-foreground">{step.description}</p>

        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setCompleted(true)}>
            {t("onboarding.skip")}
          </Button>
          <Button onClick={next}>{currentStep === steps.length - 1 ? t("onboarding.get_started") : "Далее"}</Button>
        </div>
      </div>
    </div>
  )
}
