"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { CheckCircle2, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { useAppStore } from "@/store/app-store"

const steps = [
  { key: "analyzing", label: "greeting.generation.analyzing", progress: 20 },
  { key: "scripting", label: "greeting.generation.scripting", progress: 40 },
  { key: "rendering", label: "greeting.generation.rendering", progress: 60 },
  { key: "compositing", label: "greeting.generation.compositing", progress: 75 },
  { key: "encoding", label: "greeting.generation.encoding", progress: 90 },
  { key: "finalizing", label: "greeting.generation.finalizing", progress: 100 },
]

export default function GreetingGenerationPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting } = useAppStore()
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

  useEffect(() => {
    if (currentStepIndex >= steps.length) {
      setTimeout(() => {
        updateCurrentGreeting({ status: "completed" })
        router.push("/greeting/result")
      }, 1000)
      return
    }

    const timer = setTimeout(() => {
      setCurrentStepIndex((prev) => prev + 1)
    }, 2000)
    return () => clearTimeout(timer)
  }, [currentStepIndex, router, updateCurrentGreeting])

  const currentStep = steps[currentStepIndex] || steps[steps.length - 1]
  const overallProgress = currentStepIndex >= steps.length ? 100 : steps[currentStepIndex]?.progress || 0

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <div className="flex flex-col items-center justify-center py-12 space-y-6">
          <div className="h-16 w-16 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <h1 className="text-2xl font-bold">{t("greeting.generation.title")}</h1>
          <div className="w-full max-w-sm space-y-3">
            <Progress value={overallProgress} />
            <p className="text-sm text-center text-muted-foreground">
              {currentStepIndex < steps.length ? t(currentStep.label) : t("greeting.generation.finalizing")}
            </p>
          </div>
          <div className="flex flex-col gap-2 text-sm text-muted-foreground">
            {steps.map((step, index) => (
              <div key={step.key} className="flex items-center gap-2">
                {index <= currentStepIndex ? (
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                ) : (
                  <Loader2 className="h-4 w-4 animate-spin opacity-30" />
                )}
                <span className={index <= currentStepIndex ? "text-foreground" : ""}>
                  {t(step.label)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
