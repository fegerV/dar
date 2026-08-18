"use client"

import { useTranslation } from "react-i18next"
import { CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface StepperProps {
  steps: string[]
  currentStep: number
}

export function Stepper({ steps, currentStep }: StepperProps) {
  const { t } = useTranslation()

  return (
    <div className="flex items-center justify-between w-full mb-8">
      {steps.map((step, index) => {
        const isActive = index === currentStep
        const isCompleted = index < currentStep
        return (
          <div key={step} className="flex items-center flex-1">
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors",
                  isCompleted && "border-primary bg-primary text-primary-foreground",
                  isActive && "border-primary bg-primary text-primary-foreground",
                  !isActive && !isCompleted && "border-muted-foreground text-muted-foreground"
                )}
              >
                {isCompleted ? <CheckCircle2 className="h-5 w-5" /> : index + 1}
              </div>
              <span
                className={cn(
                  "mt-2 text-xs text-center hidden sm:block",
                  isActive || isCompleted ? "text-foreground font-medium" : "text-muted-foreground"
                )}
              >
                {t(step)}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "h-0.5 flex-1 mx-2 transition-colors",
                  isCompleted ? "bg-primary" : "bg-muted"
                )}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
