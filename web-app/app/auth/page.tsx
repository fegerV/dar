"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { register } from "@/lib/api"

export default function AuthPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [step, setStep] = useState<"register" | "login">("register")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      await register(email, password, displayName || undefined)
      router.push("/onboarding/about-me")
    } catch (err: any) {
      const msg = err?.message || t("auth.register_error")
      if (msg.includes("already exists")) {
        setStep("login")
        setError(t("auth.already_have_account_prompt"))
      } else {
        setError(msg)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      const { login } = await import("@/lib/api")
      await login(email, password)
      router.push("/onboarding/about-me")
    } catch (err: any) {
      setError(err?.message || t("auth.login_error"))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <button
          onClick={() => router.back()}
          className="flex items-center text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>

        <div className="space-y-2">
          <h1 className="text-2xl font-bold">
            {step === "register" ? t("auth.register_title") : t("auth.login_title")}
          </h1>
          <p className="text-sm text-muted-foreground">
            {step === "register" ? t("auth.register_subtitle") : t("auth.login_subtitle")}
          </p>
        </div>

        {error && (
          <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
            {error}
          </div>
        )}

        <form
          onSubmit={step === "register" ? handleRegister : handleLogin}
          className="space-y-4"
        >
          <div className="space-y-2">
            <Label htmlFor="email">{t("auth.email_label")}</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder={t("auth.email_placeholder")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          {step === "register" && (
            <div className="space-y-2">
              <Label htmlFor="display_name">{t("auth.name_label")}</Label>
              <Input
                id="display_name"
                type="text"
                autoComplete="name"
                placeholder={t("auth.name_placeholder")}
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                disabled={isLoading}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="password">{t("auth.password_label")}</Label>
            <Input
              id="password"
              type="password"
              autoComplete={step === "register" ? "new-password" : "current-password"}
              placeholder={t("auth.password_placeholder")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          {step === "register" && (
            <p className="text-xs text-muted-foreground">
              {t("auth.password_hint")}
            </p>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading
              ? t("common.loading")
              : step === "register"
                ? t("auth.register_button")
                : t("auth.login_button")}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          {step === "register" ? (
            <>
              {t("auth.have_account")}{" "}
              <button
                onClick={() => setStep("login")}
                className="text-primary hover:underline"
              >
                {t("auth.login_link")}
              </button>
            </>
          ) : (
            <>
              {t("auth.no_account")}{" "}
              <button
                onClick={() => setStep("register")}
                className="text-primary hover:underline"
              >
                {t("auth.register_link")}
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  )
}
