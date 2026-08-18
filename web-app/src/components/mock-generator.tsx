"use client"

import { useCallback, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { CheckCircle2, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface PhotoQuality {
  url: string
  score: number
  isBest?: boolean
}

interface MockGeneratorProps {
  photos: string[]
  onComplete: (bestIndex: number) => void
}

export function MockGenerator({ photos, onComplete }: MockGeneratorProps) {
  const { t } = useTranslation()
  const [qualities, setQualities] = useState<PhotoQuality[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(true)

  useEffect(() => {
    if (photos.length === 0) return
    setIsAnalyzing(true)
    const scores = photos.map(() => Math.floor(Math.random() * 41) + 60)
    const maxScore = Math.max(...scores)
    const qualityData = photos.map((url, i) => ({
      url,
      score: scores[i],
      isBest: scores[i] === maxScore,
    }))
    const timer = setTimeout(() => {
      setQualities(qualityData.sort((a, b) => b.score - a.score))
      setIsAnalyzing(false)
    }, 1500)
    return () => clearTimeout(timer)
  }, [photos])

  const handleAutoSelect = useCallback(() => {
    const bestIndex = qualities.findIndex((q) => q.isBest)
    if (bestIndex !== -1) onComplete(bestIndex)
  }, [qualities, onComplete])

  if (isAnalyzing) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
        <p className="text-muted-foreground">Анализируем качество фото...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {qualities.map((q, index) => (
          <div
            key={index}
            className={cn(
              "relative rounded-lg overflow-hidden border-2 transition-all",
              q.isBest ? "border-primary ring-2 ring-primary/20" : "border-muted"
            )}
          >
            <div className="aspect-square">
              <img src={q.url} alt={`Photo ${index + 1}`} className="w-full h-full object-cover" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white p-2 flex items-center justify-between">
              <span className="text-xs font-medium">Качество: {q.score}</span>
              {q.isBest && <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />}
            </div>
            {q.isBest && (
              <div className="absolute top-2 left-2">
                <Badge className="bg-primary text-xs">{t("onboarding.quality_check.best")}</Badge>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="flex gap-3">
        <Button onClick={handleAutoSelect} className="flex-1">
          {t("onboarding.quality_check.auto_select")}
        </Button>
      </div>
    </div>
  )
}

