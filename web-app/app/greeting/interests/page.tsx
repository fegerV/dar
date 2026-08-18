"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { TagSelector } from "@/components/tag-selector"
import { Textarea } from "@/components/ui/textarea"
import { useAppStore } from "@/store/app-store"

const interestsOptions = [
  "футбол", "кино", "музыка", "путешествия", "книги", "игры",
  "технологии", "искусство", "спорт", "кулинария", "мода", "автомобили",
  "фотография", "танцы", "рыбалка", "охота", "садоводство", "фильмы",
]

export default function GreetingInterestsPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { updateCurrentGreeting } = useAppStore()
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [customNotes, setCustomNotes] = useState("")

  const handleNext = () => {
    updateCurrentGreeting({ interests: selectedInterests, customNotes })
    router.push("/greeting/mood")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.interests.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.interests.subtitle")}</p>

        <div className="space-y-6">
          <div className="space-y-2">
            <Label>{t("greeting.interests.interests_label")}</Label>
            <TagSelector
              tags={interestsOptions}
              selected={selectedInterests}
              onToggle={(tag) => {
                setSelectedInterests((prev) =>
                  prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
                )
              }}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">{t("greeting.interests.notes_label")}</Label>
            <Textarea
              id="notes"
              placeholder={t("greeting.interests.notes_placeholder")}
              value={customNotes}
              onChange={(e) => setCustomNotes(e.target.value)}
              rows={4}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => router.back()} className="flex-1">
              {t("common.back")}
            </Button>
            <Button onClick={handleNext} className="flex-1">
              {t("greeting.interests.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
