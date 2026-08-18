"use client"

import { useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ConceptCard } from "@/components/concept-card"
import { useAppStore } from "@/store/app-store"

const mockConcepts: { id: string; title: string; description: string; tags: string[] }[] = [
  { id: "1", title: "concept.epic", description: "Эпическое открытие с драматичным lighting и кадром на весь экран. Герой в центре внимания, эффект присутствия.", tags: ["cinematic", "epic", "dramatic"] },
  { id: "2", title: "concept.comedy", description: "Забавная сцена с неожиданным поворотом и харизматичным персонажем. Юмор и энергия.", tags: ["funny", "energetic", "surprise"] },
  { id: "3", title: "concept.elegant", description: "Изысканная визуальная история с плавными переходами и утончённой цветовой палитрой.", tags: ["elegant", "minimal", "style"] },
]

export default function GreetingConceptsPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting, state } = useAppStore()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [concepts, setConcepts] = useState(mockConcepts)

  const handleRegenerate = () => {
    setConcepts([
      { id: Date.now().toString(), title: "concept.new_" + Date.now(), description: "Новая уникальная концепция с неожиданными поворотами и яркими образами.", tags: ["unique", "fresh", "creative"] },
      { id: (Date.now() + 1).toString(), title: "concept.another_" + Date.now(), description: "Альтернативный взгляд на праздник с юмором и теплом.", tags: ["warm", "funny", "alternative"] },
      { id: (Date.now() + 2).toString(), title: "concept.third_" + Date.now(), description: "Кинематографичный рассказ с глубоким смыслом и красивыми кадрами.", tags: ["cinematic", "deep", "beautiful"] },
    ])
    setSelectedId(null)
  }

  const handleNext = () => {
    if (selectedId) {
      const selected = concepts.find((c) => c.id === selectedId)
      updateCurrentGreeting({ selectedConceptId: selectedId, concepts })
      router.push("/greeting/text")
    }
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.concepts.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.concepts.subtitle")}</p>

        <div className="space-y-4 mb-6">
          {concepts.map((concept) => (
            <ConceptCard
              key={concept.id}
              concept={concept}
              selected={selectedId === concept.id}
              onClick={() => setSelectedId(concept.id)}
            />
          ))}
        </div>

        <div className="flex gap-3">
          <Button variant="outline" onClick={handleRegenerate} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            {t("greeting.concepts.regenerate")}
          </Button>
          <Button variant="outline" onClick={() => router.back()}>{t("common.back")}</Button>
          <Button onClick={handleNext} disabled={!selectedId} className="flex-1">
            {t("greeting.concepts.next")}
          </Button>
        </div>
      </div>
    </div>
  )
}
