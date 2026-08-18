"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight, CreditCard, Coins } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { useAppStore } from "@/store/app-store"

export default function GreetingPaymentPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, updateCurrentGreeting } = useAppStore()
  const [useBonus, setUseBonus] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)

  const price = 990
  const bonus = useBonus ? 100 : 0
  const total = price - bonus

  const handlePay = async () => {
    setProcessing(true)
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval)
          return 100
        }
        return p + 10
      })
    }, 200)

    setTimeout(() => {
      setProcessing(false)
      updateCurrentGreeting({
        payment: { amount: total, currency: "RUB", method: "card", status: "completed", bonusUsed: bonus },
        status: "generating",
      })
      router.push("/greeting/generation")
    }, 2500)
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.payment.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.payment.subtitle")}</p>

        <Card>
          <CardHeader>
            <CardTitle>Заказ</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span>{t("greeting.payment.price")}</span>
              <span className="font-medium">{price} ₽</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Coins className="h-4 w-4 text-yellow-500" />
                <span>{t("greeting.payment.bonus")}</span>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={useBonus}
                  onCheckedChange={(checked) => setUseBonus(checked as boolean)}
                />
                <span className="text-sm">-100 ₽</span>
              </div>
            </div>
            <div className="border-t pt-3 flex justify-between text-lg font-semibold">
              <span>{t("greeting.payment.total")}</span>
              <span>{total} ₽</span>
            </div>
          </CardContent>
        </Card>

        {processing && (
          <div className="mt-6 space-y-2">
            <Progress value={progress} />
            <p className="text-sm text-muted-foreground text-center">Обработка платежа...</p>
          </div>
        )}

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} disabled={processing} className="flex-1">
            {t("common.back")}
          </Button>
          <Button onClick={handlePay} disabled={processing} className="flex-1 flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            {processing ? `${progress}%` : t("greeting.payment.pay")}
          </Button>
        </div>
      </div>
    </div>
  )
}

