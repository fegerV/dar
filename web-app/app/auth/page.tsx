"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function AuthPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [step, setStep] = useState<"phone" | "code">("phone")

  const handleSendCode = () => {
    if (phone.length >= 10) setStep("code")
  }

  const handleVerify = () => {
    if (code.length >= 4) {
      router.push("/onboarding/about-me")
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">{t("auth.title")}</h1>
        </div>

        {step === "phone" && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="phone">{t("auth.phone_label")}</Label>
              <Input
                id="phone"
                type="tel"
                placeholder={t("auth.phone_placeholder")}
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <Button className="w-full" onClick={handleSendCode}>
              {t("auth.send_code")}
            </Button>
          </div>
        )}

        {step === "code" && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code">{t("auth.code_label")}</Label>
              <Input
                id="code"
                type="text"
                inputMode="numeric"
                maxLength={4}
                placeholder={t("auth.code_placeholder")}
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </div>
            <Button className="w-full" onClick={handleVerify}>
              {t("auth.verify")}
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              Введите любой 4-значный код
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
