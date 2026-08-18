"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { OptionCard } from "@/components/option-card"
import { useAppStore } from "@/store/app-store"

const templates = [
  { id: "1", title: "template.classic", description: "Классический видеоролик с анимацией" },
  { id: "2", title: "template.modern", description: "Современный стиль с динамичными переходами" },
  { id: "3", title: "template.minimal", description: "Минималистичный и элегантный" },
]

export default function GreetingTemplatePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting } = useAppStore()
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)

  const handleNext = () => {
    if (selectedTemplate) {
      updateCurrentGreeting({
        template: { id: selectedTemplate, title: templates.find((t) => t.id === selectedTemplate)!.title, description: templates.find((t) => t.id === selectedTemplate)!.description },
      })
      router.push("/greeting/review")
    }
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.template.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.template.subtitle")}</p>

        <div className="space-y-3">
          {templates.map((template) => (
            <OptionCard
              key={template.id}
              title={template.title}
              description={template.description}
              selected={selectedTemplate === template.id}
              onClick={() => setSelectedTemplate(template.id)}
            />
          ))}
        </div>

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} className="flex-1">
            {t("common.back")}
          </Button>
          <Button onClick={handleNext} disabled={!selectedTemplate} className="flex-1">
            {t("greeting.template.next")}
          </Button>
        </div>
      </div>
    </div>
  )
}
