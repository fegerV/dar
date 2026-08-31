"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Rating } from "@/components/rating"
import { useAppStore } from "@/store/app-store"

export default function GreetingRatingPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, rateGreeting, completeCurrentGreeting } = useAppStore()
  const [rating, setRating] = useState(0)
  const [feedback, setFeedback] = useState("")

  const handleSubmit = () => {
    if (state.currentGreeting) {
      rateGreeting(state.currentGreeting.id, rating as 1 | 2 | 3 | 4 | 5, feedback)
      completeCurrentGreeting()
    }
    router.push("/home")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.rating.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.rating.subtitle")}</p>

        <div className="space-y-6">
          <div className="flex flex-col items-center gap-4">
            <Rating value={rating} onChange={setRating} size={40} />
            <p className="text-sm text-muted-foreground">
              {rating === 0 && "Оцените результат"}
              {rating === 1 && "Очень плохо"}
              {rating === 2 && "Плохо"}
              {rating === 3 && "Нормально"}
              {rating === 4 && "Хорошо"}
              {rating === 5 && "Отлично!"}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="feedback">{t("greeting.rating.feedback_placeholder").replace(" (необязательно)", "")}</Label>
            <Textarea
              id="feedback"
              placeholder={t("greeting.rating.feedback_placeholder")}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
            />
          </div>

          <Button onClick={handleSubmit} disabled={rating === 0} className="w-full">
            {t("greeting.rating.submit")}
          </Button>
        </div>
      </div>
    </div>
  )
}
