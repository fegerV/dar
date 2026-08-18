"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { TagSelector } from "@/components/tag-selector"
import { useAppStore } from "@/store/app-store"

const personalities = [
  "весёлый", "серьёзный", "романтичный", "практичный",
  "творческий", "спортивный", "интеллектуальный", "романтик",
  "оптимист", "реалист", "экстраверт", "интроверт",
]

export default function GreetingRelationshipPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting, state } = useAppStore()
  const [relationship, setRelationship] = useState("")
  const [selectedPersonality, setSelectedPersonality] = useState<string[]>([])

  const handleNext = () => {
    updateCurrentGreeting({ relationship, personality: selectedPersonality })
    router.push("/greeting/interests")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.relationship.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.relationship.subtitle")}</p>

        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="relationship">{t("greeting.relationship.relationship_label")}</Label>
            <Input
              id="relationship"
              placeholder={t("greeting.relationship.relationship_placeholder")}
              value={relationship}
              onChange={(e) => setRelationship(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>{t("greeting.relationship.personality_label")}</Label>
            <TagSelector
              tags={personalities}
              selected={selectedPersonality}
              onToggle={(tag) => {
                setSelectedPersonality((prev) =>
                  prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
                )
              }}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleNext} className="flex-1">
              {t("greeting.relationship.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
