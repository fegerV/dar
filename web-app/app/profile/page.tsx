"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, User, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { BottomNav } from "@/components/bottom-nav"
import { useAppStore } from "@/store/app-store"

export default function ProfilePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, deleteRecipient } = useAppStore()

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-3xl font-bold mb-6">{t("profile.title")}</h1>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                {t("profile.title")}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm">
                <span className="font-medium">Пол:</span> {state.user.gender || "Не указан"}
              </p>
              <p className="text-sm">
                <span className="font-medium">Возраст:</span> {state.user.age || "Не указан"}
              </p>
              <p className="text-sm">
                <span className="font-medium">Фото:</span> {state.user.photos.length} шт.
              </p>
              <Button variant="outline" className="w-full" onClick={() => router.push("/onboarding/about-me")}>
                {t("profile.edit_profile")}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("profile.my_recipients")}</CardTitle>
            </CardHeader>
            <CardContent>
              {state.recipients.length === 0 ? (
                <p className="text-sm text-muted-foreground">{t("profile.no_recipients")}</p>
              ) : (
                <div className="space-y-2">
                  {state.recipients.map((recipient) => (
                    <div key={recipient.id} className="flex items-center justify-between p-2 rounded-md border">
                      <div>
                        <p className="font-medium text-sm">{recipient.name}</p>
                        <p className="text-xs text-muted-foreground">{recipient.relationship || "Без отношения"}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteRecipient(recipient.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
              <Button
                variant="outline"
                className="w-full mt-4"
                onClick={() => router.push("/greeting/who")}
              >
                {t("profile.add_recipient")}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
      <BottomNav />
    </div>
  )
}
