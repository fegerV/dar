"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft, Users, UserPlus } from "lucide-react"
import { useAppStore } from "@/store/app-store"

export default function GreetingWhoPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, updateCurrentGreeting } = useAppStore()

  const selectRecipient = (recipientId: string) => {
    const recipient = state.recipients.find((r) => r.id === recipientId)
    if (recipient) {
      updateCurrentGreeting({
        id: Date.now().toString(),
        recipientId: recipient.id,
        recipientName: recipient.name,
        recipientAge: recipient.age,
        recipientGender: recipient.gender,
        occasion: "birthday",
        mood: "wow",
        concepts: [],
        status: "draft",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      })
      router.push("/greeting/occasion")
    }
  }

  const createNew = () => {
    updateCurrentGreeting({
      id: Date.now().toString(),
      occasion: "birthday",
      mood: "wow",
      concepts: [],
      status: "draft",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    })
    router.push("/greeting/recipient")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("greeting.who.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("greeting.who.subtitle")}</p>

        {state.recipients.length > 0 && (
          <div className="space-y-3 mb-6">
            <h3 className="text-sm font-medium text-muted-foreground">{t("greeting.who.select_existing")}</h3>
            {state.recipients.map((recipient) => (
              <div
                key={recipient.id}
                className="p-4 rounded-lg border cursor-pointer hover:border-primary/50 transition-colors"
                onClick={() => selectRecipient(recipient.id)}
              >
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{recipient.name}</p>
                    <p className="text-sm text-muted-foreground">{recipient.relationship || "Без отношения"}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div
          className="p-4 rounded-lg border-2 border-dashed cursor-pointer hover:border-primary/50 transition-colors flex items-center gap-3"
          onClick={createNew}
        >
          <UserPlus className="h-5 w-5 text-primary" />
          <span className="font-medium">{t("greeting.who.create_new")}</span>
        </div>
      </div>
    </div>
  )
}
